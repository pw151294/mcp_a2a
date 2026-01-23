import asyncio
import logging
import uuid
from abc import ABC
from typing import Optional, List, AsyncGenerator, Dict, Any

from app.domain.external.json_parser import JsonParser
from app.domain.external.llm import LLM
from app.domain.models.app_config import AgentConfig
from app.domain.models.event import Event, ToolEvent, ToolEventStatus, ErrorEvent, MessageEvent
from app.domain.models.memory import Memory
from app.domain.models.message import Message
from app.domain.models.tool_result import ToolResult
from app.domain.services.tools.base import BaseTool

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """基础Agent智能体"""
    name: str = ""  # 智能体的名称
    _system_prompt: str = ""  # 系统预设提示词
    _format: Optional[str] = None  # Agent响应格式
    _retry_interval: float = 1.0  # 重试间隔
    _tool_choice: Optional[str] = None  # 强制选择工具

    def __init__(self,
                 agent_config: AgentConfig,  # agent配置
                 llm: LLM,  # 语言模型协议
                 memory: Memory,  # 记忆
                 json_parser: JsonParser,  # json输出解析器
                 tools: List[BaseTool]):  # 工具列表
        self._agent_config = agent_config
        self._llm = llm
        self._memory = memory
        self._json_parser = json_parser
        self._tools = tools

    def _get_available_tools(self) -> List[Dict[str, str]]:
        """获取Agent所有可用的工具列表参数声明/Schema"""
        available_tools = []
        for tool in self._tools:
            available_tools.extend(tool.get_tools())
        return available_tools

    def _get_tool(self, tool_name: str) -> BaseTool:
        """获取对应工具所在的provider"""
        # 循环遍历所有的工具包
        for tool in self._tools:
            # 判断工具包中是否存在该工具
            if tool.has_tool(tool_name):
                return tool
        raise ValueError(f"{tool_name} not found")

    async def _add_to_memory(self, messages: List[Dict[str, Any]]) -> None:
        """将对应的信息添加到记忆中"""
        # 检查记忆的消息是否为空，如果是空的话就需要添加预设的提示词作为初始记忆
        if self._memory.empty:
            self._memory.add_message({
                "role": "system", "content": self._system_prompt
            })

        # 将正常消息添加到memory中
        self._memory.add_messages(messages)

    async def _invoke_tool(self, tool: BaseTool, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """传递工具包+工具名字+对应的参数调用指定的工具"""
        # 执行循环调用工具获取结果
        err = ""
        for _ in range(self._agent_config.max_retries):
            try:
                return await tool.invoke(tool_name, **arguments)
            except Exception as ex:
                err = str(ex)
                logger.exception(f"调用工具{tool_name}出错：{str(ex)}")
                await asyncio.sleep(self._retry_interval)
                continue

        # 循环最大重试次数后没有结果 则将错误作为工具的执行结果 让LLM自行处理
        return ToolResult(success=False, message=err)

    async def _invoke_llm(self, messages: List[Dict[str, Any]], format: Optional[str] = None) -> Dict[str, Any]:
        """"调用语言模型并处理记忆内容"""
        # 将消息添加到记忆中
        await self._add_to_memory(messages)

        # 组装语言模型的响应格式
        response_format = {"type": format} if format else None

        # 循环向LLM发起提问直到最大的重试次数
        for _ in range(self._agent_config.max_retries):
            try:
                # 调用语言模型获取响应内容
                message = self._llm.invoke(
                    message=messages,
                    response_format=response_format,
                    tools=self._get_available_tools(),
                    tool_choice=self._tool_choice,
                )

                # 处理AI响应内容避免空回复
                if message.get("role") == "assistant":
                    if not message.get("content") and not message.get("tool_calls"):
                        logger.warning("LLM回复了空内容，执行重试")
                        await self._add_to_memory([
                            {"role": "assistant", "content": ""},
                            {"role": "user", "content": "AI无响应内容，请继续"}
                        ])
                        continue

                    # 取出非空消息并处理工具调用
                    filtered_message = {"role": "assistant", "content": message.get("content")}
                    if message.get("tool_calls"):
                        # 取出工具调用的数据 限制LLM一次只能调用工具
                        filtered_message["tool_calls"] = message.get("tool_calls")
                else:
                    # 非AI消息 记录日志并存储message
                    logger.warning(f"LLM响应内容无法确认消息角色：{message.get('role')}")
                    filtered_message = message
                # 将消息添加到消息列表
                await self._add_to_memory([filtered_message])
            except Exception as e:
                # 记录日志并睡眠指定的时间
                logger.error(f"调用大模型对话失败：{str(e)}")
                await asyncio.sleep(self._retry_interval)

    async def invoke(self, query: str, format: Optional[str] = None) -> AsyncGenerator[Event, None]:
        """传递消息+响应格式 调用程序生成异步迭代内容"""
        # 判断是否传递了format
        format = format if format else self._format

        # 调用语言模型获取内容
        message = await self._invoke_llm(
            messages=[{"role": "user", "content": query}],
            format=format
        )

        # 循环遍历知道最大的迭代次数
        for _ in range(self._agent_config.max_iterations):
            # 如果响应的内容无工具调用则表示LLM生成了文本回答 这时候就是最终答案
            if not message.get("tool_calls"):
                break

            # 循环遍历工具参数并执行
            tool_messages = []
            for tool_call in message["tool_calls"]:
                if not tool_call.get("function"):
                    continue

                # 取出工具调用的ID、名字还有参数信息
                tool_call_id = tool_call["id"] or str(uuid.uuid4())
                function_name = tool_call["function"]["name"]
                function_args = await self._json_parser.invoke(tool_call["function"]["arguments"])

                # 取出Agent中对应的工具
                tool = self._get_tool(function_name)

                # 返回工具即将调用事件 其中tool_content需要在具体的业务中实现
                yield ToolEvent(
                    tool_call_id=tool_call_id,
                    tool_name=tool.name,
                    function_name=function_name,
                    function_args=function_args,
                    status=ToolEventStatus.CALLING
                )

                # 调用工具并获取结果
                result = await self._invoke_tool(tool, function_name, function_args)

                # 返回工具调用结果 其中tool_content需要在业务中实现
                yield ToolEvent(
                    tool_call_id=tool_call_id,
                    function_name=function_name,
                    function_args=function_args,
                    function_result=result,
                    status=ToolEventStatus.CALLED
                )

                # 组装工具响应
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "function_name": function_name,
                    "content": result.model_dump()
                })

            # 所有工具都执行完成之后 调用LLM获取汇总消息二次提问
            message = await self._invoke_llm(tool_messages)

        else:
            # 超过最大迭代次数 则抛出错误
            yield ErrorEvent(error=f"Agent迭代达到最大次数：{self._agent_config.max_iterations}")

        # 在指定的步骤内完成了迭代 则返回消息事件
        yield MessageEvent(message=message["content"])

    async def compact_memory(self) -> None:
        """压缩Agent记忆"""
        self._memory.compact()

    async def roll_back(self, message: Message) -> None:
        """Agent状态回滚，该函数用来确保Agent的消息列表状态是正确的，用来发送新的消息，暂停/停止任务，通知用户"""
        # 1 取出记忆中的最后一条消息 检查是否是工具调用消息
        last_message = self._memory.get_last_message()
        if (
                not last_message or
                not last_message.get("tool_calls") or
                len(last_message.get("tool_calls")) == 0
        ):
            return

        # 取出消息中的工具调用参数
        tool_call = last_message.get("tool_calls")[0]

        # 提取出工具名称还有ID
        function_name = tool_call.get("function", {}).get("name")
        tool_call_id = tool_call["id"]

        # 判断当前工具下是不是通知用户的消息
        if function_name == "message_ask_user":
            self._memory.add_message({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "function_name": function_name,
                "content": message.model_dump_json()
            })
        else:
            # 否则直接删除最后一条消息
            self._memory.roll_back()

    @property
    def memory(self) -> Memory:
        """只读属性 返回记忆"""
        return self._memory
