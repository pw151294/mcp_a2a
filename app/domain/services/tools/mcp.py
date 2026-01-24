"""
MCP客户端管理器的开发思路：
1.在AGent执行的过程中，有可能需要多次调用工具
    但是在MCP工具的每次获取都需要调用客户端会话的list_tools()方法
    因此需要缓存工具的参数信息，在初始化的时候调用一次，在销毁MCP客户端管理器的时候一并清除
2.在前端UI交互中，无论MCP服务是否启动，都会显示工具列表信息
    在Agent执行的过程中只会传递已启动的MCP服务
    对于MCP客户端管理器来说，可以根据接收的MCP配置差异加载不同的服务器
    而不是仅从配置文件里读取数据
3.MCP客户端管理需要同时管理多个MCP服务，支持不同的传输协议，需要根据传输协议的不同来创建会话客户端，缓存会话
4.有一些环境变量存储在整个系统，在初始化MCP服务的时候，需要将传递进来的环境变量与系统的环境变量进行合并后传递给MCP服务
5.使用AsyncExitsStack异步上下文管理器来管理上下文，避免使用with多层嵌套
6.MCPClientManager初始化非常耗时，所以需要有机制可以判断避免重复初始化
7.config.yaml是直接暴露在项目中的，所以在使用config.yaml初始化的时候必须做二次校验
8.同时缓存ClientSession+ToolSchema，一个是客户端会话，一个是工具参数声明
9.MCP客户端管理在清除/停止使用的时候必须关闭异步上下文管理器、清除资源（ClientSession + ToolSchema）
"""
import logging
import os
from contextlib import AsyncExitStack
from typing import Optional, Dict, List, Any, Awaitable

from mcp import ClientSession, Tool, StdioServerParameters, stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from app.domain.models.app_config import McpConfig, McpServerConfig, McpTransport
from app.domain.models.tool_result import ToolResult
from app.domain.services.tools.base import BaseTool

logger = logging.getLogger(__name__)


class McpClientManager:
    """MCP客户端管理器"""

    def __init__(self, mcp_config: Optional[McpConfig] = None) -> None:
        """构造函数 完成MCP客户端管理器的初步初始化"""
        self._mcp_config: McpConfig = mcp_config  # MCP配置信息
        self._exist_stack: AsyncExitStack = AsyncExitStack()  # 异步上下文管理器
        self._clients: Dict[str, ClientSession] = {}  # 缓存的客户端上下文
        self._tools: Dict[str, List[Tool]] = {}  # 缓存的MCP工具参数说明
        self._initialized: bool = False  # 是否初始化标识

    @property
    def tools(self) -> Dict[str, List[Tool]]:
        """只读属性 返回缓存的MCP工具参数声明 建就是服务的名字 值就是服务对应的工具声明"""
        return self._tools

    async def initialize(self) -> None:
        """初始化函数 用来连接所有配置的MCP服务器"""
        if self._initialized:
            return

        try:
            # 记录日志并连接MCP服务器
            logger.info(f"从config.yaml里加载了{len(self._mcp_config.mcpServers)}个MCP服务器")
            await self._connect_mcp_servers()
            self._initialized = True
            logger.info(f"MCP客户端管理器加载成功")
        except Exception as e:
            logger.error(f"MCP客户端管理器加载失败：{str(e)}")
            raise

    async def _connect_mcp_servers(self) -> None:
        """根据配置连接所有的MCP服务器"""
        # 循环遍历传递进来的所有MCP服务器
        for server_name, server_config in self._mcp_config.mcpServers.items():
            try:
                # 根据服务名称+服务配置连接到MCP服务器
                await self._connect_mcp_server(server_name, server_config)
            except Exception as e:
                logger.error(f"连接MCP服务器{server_name}失败：{str(e)}")
                continue

    async def _connect_mcp_server(self, server_name: str, server_config: McpServerConfig) -> None:
        """根据传递的服务名字+服务配置连接到单个MCP服务"""
        try:
            # 获取MCP服务的传输协议
            transport = server_config.transport

            # 根据不同的传输协议调用不同的方法连接到MCP服务器
            if transport == McpTransport.STDIO:
                await self._connect_stdio_server(server_name, server_config)
            elif transport == McpTransport.SSE:
                await self._connect_sse_server(server_name, server_config)
            elif transport == McpTransport.STREAMABLE_HTTP:
                await self._connect_streamable_http_server(server_name, server_config)
            else:
                raise ValueError(f"MCP服务{server_name}使用了不支持的传输协议：{transport}")
        except Exception as e:
            logger.error(f"连接MCP服务器{server_name}出错：{str(e)}")
            raise e

    async def _connect_stdio_server(self, server_name: str, server_config: McpServerConfig) -> None:
        """根据服务的名称+配置连接stdio服务"""
        # 从配置里提取相关的命令信息
        command = server_config.command
        args = server_config.args
        env = server_config.env

        # 检查command是否存在
        if not command:
            raise ValueError("连接stdio-mcp服务需要配置command指令")

        # 构建stdio连接参数
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env={**os.environ, **env},
        )

        try:
            # 使用异步上下文管理器创建传输协议
            stdio_transport = await self._exist_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = stdio_transport

            # 根据读取和写入流构建会话
            session: ClientSession = await self._exist_stack.enter_async_context(
                ClientSession(read_stream=read_stream, write_stream=write_stream)
            )

            # 初始化MCP服务会话
            assert session.initialize()

            # 缓存对应的MCP服务客户端
            self._clients[server_name] = session

            # 缓存对应的MCP工具列表
            await self._cache_mcp_server_tools(server_name, session)
            logger.info(f"连接stdio-mcp服务器成功")
        except Exception as e:
            logger.error(f"连接stdio-mcp服务器失败：{str(e)}")
            raise

    async def _connect_sse_server(self, server_name: str, server_config: McpServerConfig) -> None:
        """根据服务名字+配置连接sse服务"""
        # 根据sse服务器的连接url并判断是否存在
        url = server_config.url
        if not url:
            raise ValueError("连接sse-mcp服务器需要配置url")

        try:
            sse_transport = await self._exist_stack.enter_async_context(
                sse_client(url=url, header=server_config.headers),
            )
            read_stream, write_stream = sse_transport

            # 创建客户端上下文
            session: ClientSession = await self._exist_stack.enter_async_context(
                ClientSession(read_stream=read_stream, write_stream=write_stream)
            )
            await session.initialize()

            # 初始化对应的缓存工具
            self._clients[server_name] = session

            # 缓存对应的MCP工具列表
            await self._cache_mcp_server_tools(server_name, session)
            logger.info(f"连接sse-mcp服务器成功")
        except Exception as e:
            logger.error(f"连接sse-mcp服务失败：{str(e)}")
            raise

    async def _connect_streamable_http_server(self, server_name: str, server_config: McpServerConfig) -> None:
        """根据配置名字+配置连接streamable-http服务"""
        # 提取streamable-http服务器的连接url并判断是否存在
        url = server_config.url
        if not url:
            raise ValueError("连接sse-mcp服务器需要配置的url")

        try:
            # 连接streamable-http服务器
            streamable_http_transport = await self._exist_stack.enter_async_context(
                streamable_http_client(url=url),
            )
            read_stream, write_stream, _ = streamable_http_transport

            # 创建客户端上下文
            session: ClientSession = await self._exist_stack.enter_async_context(
                ClientSession(read_stream=read_stream, write_stream=write_stream)
            )
            await session.initialize()

            # 初始化对应的缓存工具
            self._clients[server_name] = session

            # 缓存对应的MCP工具列表
            await self._cache_mcp_server_tools(server_name, session)
            logger.info(f"连接streamable-http-mcp服务器成功")
        except Exception as e:
            logger.error(f"连接streamable-http-mcp服务失败：{str(e)}")
            raise e

    async def _cache_mcp_server_tools(self, server_name: str, session: ClientSession) -> None:
        """根据传递的服务名称+会话缓存MCP服务工具列表"""
        try:
            tool_response = await session.list_tools()
            tools = tool_response.tools if tool_response else []
            self._tools[server_name] = tools
            logger.info(f"MCP服务器{server_name}提供了{len(tools)}个工具")
        except Exception as e:
            logger.error(f"获取MCP服务器{server_name}的工具列表失败：{str(e)}")
            self._tools[server_name] = []

    async def get_all_tools(self) -> List[Dict[str, Any]]:
        """获取所有的MCP工具列表，返回LLM可以使用的工具参数声明列表并处理MCP的名字"""
        # 定义一个变量存储所有的结果
        all_tools = []

        # 循环遍历所有缓存的工具
        for server_name, tools in self._tools.items():
            # 循环取出每个MCP的工具列表
            for tool in tools:
                # 修改工具的名字加上MCP前缀+服务名字
                if server_name.startswith("mcp_"):
                    tool_name = f"{server_name}_{tool.name}"
                else:
                    tool_name = f"mcp_{server_name}_{tool.name}"

                # 生成OpenAI工具描述
                tool_schema = {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": f"[{server_name} {tool.description or tool.name}]",
                        "parameters": tool.inputSchema,
                    }
                }
                all_tools.append(tool_schema)

        return all_tools

    async def invoke(self, tool_name: str, arguments: Dict[str, Any,]) -> ToolResult:
        """根据传递的工具名字+参数调用MCP工具"""
        try:
            # 定义变量存储原始的服务名字+工具
            original_server_name = None
            original_tool_name = None

            # 循环遍历当前的所有MCP服务
            for server_name in self._mcp_config.mcpServers.keys():
                # 为server_name组装前缀
                excepted_prefix = server_name if server_name.startswith("mcp_") else f"mcp_{server_name}"

                # 判断工具名字是否以改服务为开头
                if tool_name.startswith(f"{excepted_prefix}_"):
                    original_server_name = server_name
                    original_tool_name = tool_name[len(f"{excepted_prefix}_"):]
                    break

            # 判断服务+工具是否都存在
            if not original_server_name or not original_tool_name:
                raise RuntimeError(f"服务器解析MCP工具不存在：{tool_name}")

            # 获取该工具所属的会话
            session = self._clients[original_server_name]
            if not session:
                return ToolResult(success=False, message=f"MCP服务器{original_server_name}未连接")

            # 使用会话调用工具
            result = await session.call_tool(original_tool_name, arguments)

            # 判断结果是否存在进行几个不同的操作
            if result:
                # 处理MCP工具生成的content
                content = []
                if hasattr(result, "content") and result.content:
                    for item in result.content:
                        if hasattr(item, "text"):
                            content.append(item.text)
                        else:
                            content.append(str(item))

                # 返回工具调用的结果
                return ToolResult(success=True, message="工具执行成功",
                                  data="\n".join(content) if content else "工具执行成功")
            else:
                return ToolResult(success=True, message="工具执行成功")
        except Exception as e:
            # 记录错误日志并返回失败的工具结果
            return ToolResult(
                success=False,
                message=f"工具{tool_name}调用失败：{str(e)}",
            )

    async def cleanup(self) -> None:
        """当退出MCP服务器的时候 清除对应的资源"""
        try:
            await self._exist_stack.aclose()
            self._clients.clear()
            self._tools.clear()
            self._initialized = False
            logger.info(f"清理MCP客户端管理器成功")
        except Exception as e:
            logger.error(f"清理MCP客户端管理器失败：{str(e)}")


class MCPTool(BaseTool):
    """MCP工具包 包含所有已配置+已启动的MCP配置"""
    name: str = "mcp"

    def __init__(self):
        """构造函数 完成MCP工具包的初始化"""
        super().__init__()
        self._initialized: bool = False
        self._tools = []
        self._manager = McpClientManager = None

    async def initialize(self, mcp_config: Optional[McpConfig] = None) -> None:
        """初始化MCP工具包"""
        # 判断是否初始化
        if not self._initialized:
            # 初始化MCP客户端管理器
            self._manager = McpClientManager(mcp_config=mcp_config)
            await self._manager.initialize()

            # 获取MCPServers工具列表
            self._tools = await self._manager.get_all_tools()
            self._initialized = True

    def get_tools(self) -> List[Dict[str, Any]]:
        """同步获取工具包下的所有工具列表"""
        return self._tools

    def has_tool(self, tool_name: str) -> bool:
        """传递工具名字，判断工具是否存在"""
        # 循环遍历所有的工具
        for tool in self._tools:
            # 判断工具的名字是否存在 如果是就返回True 如果不是就返回false
            if tool["function"]["name"] == tool_name:
                return True
        return False

    async def invoke(self, tool_name: str, **kwargs) -> ToolResult:
        """传递工具名字+工具参数 调用MCP工具并获取调用的结果"""
        return await self._manager.invoke(tool_name, **kwargs)

    async def cleanup(self) -> None:
        """清除MCP工具的资源"""
        if self._manager:
            self._manager.cleanup()
