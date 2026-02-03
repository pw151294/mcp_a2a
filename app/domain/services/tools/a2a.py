import logging
import uuid
from contextlib import AsyncExitStack
from typing import Optional, Dict, Any, List, Callable

import httpx

from app.domain.models.app_config import A2AConfig
from app.domain.models.tool_result import ToolResult
from app.domain.services.tools.base import BaseTool, tool

logger = logging.getLogger(__name__)

"""
A2A客户端管理器的开发思路:
1.在Agent执行过程中, 有可能需要多次调用Remote-Agent，
  但是a2a中的agent-card.json请求是网络io, 相对耗时，
  所以需要缓存agent-card的相关信息, 只有在初始化A2A客户端的时候才初始化一次,
  更新a2a服务器的时候更新, 清除a2a客户端管理器时删除;
2.在前端UI交互中, 无论A2A服务器是否启动, 都会展示Card信息,
  但是呢, 在执行/规划Agent中, 我们只传递启用的A2A服务, 所以A2A客户端管理器必须动态接受配置;
3.一个A2A客户端会同时管理多个Agent, 但是不同的A2A服务有可能他们的name是一样的，
  需要考虑传递给Agent信息时的唯一性, 会配置多一个唯一的id;
4.由于使用httpx客户端, 这个客户端需要创建上下文/释放资源, 所以可以使用AsyncExitStack来管理
  异步上下文, 避免大量使用with..as的嵌套组合;
5.A2AClientManager的初始化非常耗时, 一次请求中只初始化一次;
6.A2A配置是写在config.yaml中的并直接暴露给开发者, 有可能开发者会手动修改config.yaml
  所以在使用的时候, 最多需要做多一次校验;
7.A2A客户端管理器只实现两个方法, 一个是get_remote_agent_cards、call_remote_agent;
8.A2A客户端管理器停止时必须清除对应资源, 涵盖了缓存, 异步上下文管理器避免资源泄露;
"""


class A2AClientManager:
    """A2A客户端管理器"""

    def __init__(self, a2a_config: Optional[A2AConfig] = None) -> None:
        """完成A2A客户端的初始化"""
        self._a2a_config = a2a_config
        self._exist_stack: AsyncExitStack = AsyncExitStack()  # 上下文管理器
        self._httpx_client: Optional[httpx.AsyncClient] = None  # httpx客户端
        self._agent_card: Dict[str, Any] = {}  # agent卡片
        self._initialized: bool = False

    @property
    def agent_card(self) -> Dict[str, Any]:
        return self._agent_card

    async def initialize(self) -> None:
        """异步初始化函数，用来初始化所有已配置的A2A服务"""
        if self._initialized:
            return

        try:
            # 初始化客户端
            self._httpx_client = await self._exist_stack.enter_async_context(
                httpx.AsyncClient(timeout=600)
            )
            await self._get_a2a_agent_cards()

            # 记录日志并加载所有配置的a2a服务并获取卡片信息
            logger.info(f"加载{len(self._a2a_config.a2a_servers)}个A2A服务")
        except Exception as e:
            logger.error(f"A2A客户端管理器加载失败：{str(e)}")
            raise RuntimeError("A2A客户端管理器加载失败")

    async def _get_a2a_agent_cards(self) -> None:
        """根据配置连接所有的a2a服务获取所有的卡片信息"""
        # 循环遍历连接所有的a2a服务
        for a2a_server_config in self._a2a_config.a2a_servers:
            try:
                # 调用httpx客户端获取请求
                agent_card_response = await self._httpx_client.get(
                    f"{a2a_server_config.base_url}/.well-known/agent-card.json"
                )
                agent_card_response.raise_for_status()
                agent_card = agent_card_response.json()

                # 存储到agent_cards
                self._agent_card[a2a_server_config.id] = agent_card
            except Exception as e:
                logger.warning(f"加载A2A服务{a2a_server_config.id}失败")
                continue

    async def invoke(self, agent_id: str, query: str) -> ToolResult:
        """根据传递的智能体ID+query调用远程Agent"""
        # 判断agent_id是否存在
        if agent_id not in self._agent_card:
            return ToolResult(success=False, message="该远程Agent不存在")

        # Agent存在 取出端点信息
        agent_card = self._agent_card.get(agent_id, {})
        url = agent_card.get("url", "")

        # 判断端点是否存在
        if not url:
            return ToolResult(success=False, message="该远程Agent调用端点不存在")

        try:
            agent_response = await self._httpx_client.post(
                url,
                json={
                    "id": str(uuid.uuid4()),
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "messageId": str(uuid.uuid4()),
                            "role": "user",
                            "parts": [
                                {"kind": "text", "text": query}
                            ]
                        }
                    }
                }
            )
            agent_response.raise_for_status()

            return ToolResult(success=True, data=agent_response.json())
        except Exception as e:
            logger.error(f"远程调用Agent{agent_id}:{url}失败：{str(e)}")
            return ToolResult(success=False, message=f"远程调用Agent{agent_id}:{url}失败：{str(e)}")

    async def cleanup(self) -> None:
        """当退出A2A客户端管理器的时候需要清楚对应资源"""
        try:
            await self._exist_stack.aclose()
            self._agent_card.clear()
            self._initialized = False
            logger.info("清楚A2A客户端管理器资源成功")
        except Exception as e:
            logger.error(f"清理A2A客户端管理器失败：{str(e)}")


class A2ATool(BaseTool):
    """A2Ag工具包 根据传递配置的A2A工具包的初始化"""

    def __init__(self) -> None:
        super().__init__()
        self._initialized = False
        self.manager: Optional[A2AClientManager] = None

    async def initialize(self, a2a_config: Optional[A2AConfig]) -> None:
        """初始化A2A工具包"""
        if self._initialized:
            return

        # 初始化客户端管理器
        self.manager = A2AClientManager(a2a_config=a2a_config)
        await self.manager.initialize()
        self._initialized = True

    @tool(
        name="get_remote_agent_cards",
        description="获取可远程调用的Agent卡片信息",
        parameters={},
        required=[]
    )
    async def get_remote_agent_cards(self) -> ToolResult:
        """获取远程Agent卡片信息列表"""
        # 重组结构 将ID填充到agent_card里
        agent_cards = []
        for id, agent_card in enumerate(self.manager.agent_card.items()):
            agent_cards.append({
                "id": id,
                **agent_card
            })

        # 组装工具响应
        return ToolResult(
            success=True,
            message="获取Agent卡片信息列表成功",
            data=agent_cards
        )

    @tool(
        name="call_remote_agent",
        description="根据传递的id+query(分配给远程Agent完成的任务query)调用远程Agent完成对应需求",
        parameters={
            "id": {
                "type": "string",
                "description": "需要调用远程agent的id, 格式参考get_remote_agent_cards()返回的数据结构",
            },
            "query": {
                "type": "string",
                "description": "需要分配给该远程Agent实现的任务/需求query",
            },
        },
        required=["id", "query"],
    )
    async def call_remote_agent(self, id: str, query: str) -> ToolResult:
        """调用远程Agent并完成对应需求"""
        return await self.manager.invoke(agent_id=id, query=query)

    def _filter_parameters(cls, method: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        return super()._filter_parameters(method, kwargs)


    def get_tools(self) -> List[Dict[str, Any]]:
        return super().get_tools()


    async def invoke(self, tool_name: str, **kwargs) -> ToolResult:
        return await super().invoke(tool_name, **kwargs)


    def has_tool(self, tool_name: str) -> bool:
        return super().has_tool(tool_name)
