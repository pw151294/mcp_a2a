import logging

from typing_extensions import AsyncGenerator

from app.domain.models.event import Event, StepEventStatus, StepEvent, ToolEvent, ToolEventStatus, MessageEvent, \
    WaitEvent, ErrorEvent
from app.domain.models.file import File
from app.domain.models.message import Message
from app.domain.models.plan import Plan, Step, ExecutionStatus
from app.domain.services.agents.base import BaseAgent
from app.domain.services.prompts import SYSTEM_PROMPT, EXECUTION_PROMPT, SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent):
    """基于ReAct架构的执行Agent"""
    name: str = "react"
    _system_prompt: str = SYSTEM_PROMPT
    _format = "json_object"

    async def execute_step(self, plan: Plan, step: Step, message: Message) -> AsyncGenerator[Event, None]:
        """根据传递的消息+规划+子步骤执行相应的子步骤"""
        # 1. 根据传递的内容生成消息
        query = EXECUTION_PROMPT.format(
            message=message.message,
            attachments=message.attachments,
            language=plan.language,
            step=step.description
        )

        # 2.更新步骤的执行状态并返回Step事件
        step.status = ExecutionStatus.RUNNING
        yield StepEvent(step=step, status=StepEventStatus.STARTED)

        # 调用invoke获取Agent返回的事件内容
        async for event in self.invoke(query):
            # 判断事件类型执行不同操作
            if isinstance(event, ToolEvent):
                # 工具事件需要判断工具的名称是否等于message_ask_user
                if event.function_name == "message_ask_user":
                    # 工具如果在调用中 我们需要返回一条消息告知用户需要用户处理什么
                    if event.status == ToolEventStatus.CALLING:
                        # todo 用户message_ask_user工具还没有实现 所以参数未定 暂时定位next
                        yield MessageEvent(
                            role="assistant",
                            message=event.function_args.get("text", "")
                        )
                    elif event.status == ToolEventStatus.CALLED:
                        # 如果工具事件为已调用 则需要返回等待事件并中断程序
                        yield WaitEvent()
                        return
                    continue
            elif isinstance(event, MessageEvent):
                # 返回事件消息 意味着content有内容 content有内容说明Agent已经执行完毕
                step.status = ExecutionStatus.COMPLETED

                # message中输出的数据结构是json 需要提取并解析
                parsed_obj = await self._json_parser.invoke(event.message)
                new_step = Step.model_validate(parsed_obj)

                # 更新子步骤的数据
                step.success = new_step.success
                step.result = new_step.result
                step.attachments = new_step.attachments

                # 返回步骤完成事件
                yield StepEvent(step=step, status=StepEventStatus.COMPLETED)

                # 如果子步骤拿到了结果 还需要返回一段消息给用户
                if step.result:
                    yield MessageEvent(role="assistant", message=step.result)
                continue
            elif isinstance(event, ErrorEvent):
                # 错误事件 更新步骤的状态
                step.status = ExecutionStatus.FAILED
                step.error = event.error

                # 返回子步骤对应的事件
                yield StepEvent(step=step, status=StepEventStatus.FAILED)
            else:
                # 其他场景将事件直接返回
                yield event

        # 循环迭代之后说明子步骤已经完成 需要更新状态
        step.status = ExecutionStatus.COMPLETED

    async def summarize(self) -> AsyncGenerator[Event, None]:
        """调用Agent汇总历史的消息并生成最终的恢复+附件"""
        # 构建请求query
        query = SUMMARIZE_PROMPT

        # 调用invoke方法获取Agent生成的事件
        async for event in self.invoke(query):
            # 判断事件类型是否为消息事件 如果是则表示Agent结构化生成汇总的内容
            if isinstance(event, MessageEvent):
                # 记录日志并解析
                logger.info(f"执行Agent生成汇总内容：{event.message}")
                parsed_obj = await self._json_parser.invoke(event.message)

                # 将解析的数据转换为Message对象
                message = Message.model_validate(parsed_obj)

                # 提取消息中的附件信息
                message_attachments = message.attachments
                event_attachments = [File(filepath=fp) for fp in message_attachments]

                # 7. 返回消息事件并将消息和附件进行响应
                yield MessageEvent(
                    role="assistant",
                    message=message.message,
                    attachments=event_attachments
                )
            else:
                yield event
