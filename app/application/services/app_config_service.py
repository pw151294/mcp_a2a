from typing import List

from openai import NotFoundError

from app.domain.models.app_config import LLMConfig, AppConfig, AgentConfig, McpConfig
from app.domain.repositories.app_config_repository import AppConfigRepository
from app.domain.services.tools.mcp import McpClientManager
from app.interfaces.schemas.app_config import ListMcpServerItem


class AppConfigService:
    def __init__(self, app_config_repository: AppConfigRepository) -> None:
        """构造函数 完成依赖注入"""
        self.app_config_repository = app_config_repository

    async def _load_app_config(self) -> AppConfig:
        """加载获取所有的应用配置信息"""
        return self.app_config_repository.load()

    async def get_llm_config(self) -> LLMConfig:
        """加载LLM提供商配置信息"""
        app_config = await self._load_app_config()
        return app_config.llmconfig

    async def get_agent_config(self) -> AgentConfig:
        """加载Agent通用配置信息"""
        app_config = await self._load_app_config()
        return app_config.agent_config

    async def update_llm_config(self, llm_config: LLMConfig) -> LLMConfig:
        """根据传递的llm_config更新语言模型的供应商配置"""
        # 获取应用配置
        app_config = await self._load_app_config()

        # 判断api_key是否为空
        if not llm_config.api_key.strip():
            llm_config.api_key = app_config.llm_config.api_key

        # 调用函数更新app_config
        app_config.llm_config = llm_config
        self.app_config_repository.save(app_config)

        return app_config.llm_config

    async def update_agent_config(self, agent_config: AgentConfig) -> AgentConfig:
        """根据传递的agent_config更新Agent的通用配置"""
        # 获取Agent通用配置
        app_config = await self._load_app_config()

        # 调用函数更新app_config
        app_config.agent_config = agent_config
        self.app_config_repository.save(app_config)

        return app_config.agent_config

    async def get_mcp_servers(self) -> List[ListMcpServerItem]:
        """获取MCP服务器列表"""
        # 获取当前的应用配置
        app_config = await self._load_app_config()

        # 创建MCP客户端管理器 对配置信息部进行过滤
        mcp_servers = []
        mcp_client_manager = McpClientManager(
            mcp_config=app_config.mcp_config,
        )
        try:
            # 初始化MCP客户端管理器
            await mcp_client_manager.initialize()

            # 获取MCP客户端管理器的工具列表
            tools = mcp_client_manager.tools

            # 循环组装响应的工具格式
            for server_name, server_config in app_config.mcp_config.mcpServers.items():
                mcp_servers.append(ListMcpServerItem(
                    server_name=server_name,
                    enabled=server_config.enabled,
                    transport=server_config.transport,
                    tools=[tool.name for tool in tools.get(server_name, [])]
                ))
        finally:
            # 清除MCP客户端管理器的相关资源
            await mcp_client_manager.cleanup()

        return mcp_servers

    async def update_and_create_mcp_config(self, mcp_config: McpConfig) -> McpConfig:
        """根据传递的数据新增/更新MCP配置"""
        # 获取应用配置
        app_config = await self._load_app_config()

        # 使用新的mcp_config更新原始的配置
        app_config.mcp_config.mcpServers.update(mcp_config.mcpServers)

        # 调用数据仓库完成存储或更新
        self.app_config_repository.save(app_config)
        return app_config.mcp_config

    async def delete_mcp_server(self, server_name: str) -> McpConfig:
        """根据名字删除MCP服务"""
        app_config = await self._load_app_config()

        # 查询对应名字的MCP服务是否存在
        if server_name not in app_config.mcp_config.mcpServers:
            raise NotFoundError(f"未找到{server_name}MCP服务配置信息")

        # 如果存在就删除字典中对应的服务
        del app_config.mcp_config.mcpServers[server_name]
        self.app_config_repository.save(app_config)
        return app_config.mcp_config

    async def set_mcp_server_enabled(self, server_name: str, enabled: bool) -> McpConfig:
        """根据名称更新MCP"""
        app_config = await self._load_app_config()

        # 查询对应名字的MCP服务是否存在
        if server_name not in app_config.mcp_config.mcpServers:
            raise NotFoundError(f"未找到{server_name}MCP服务配置信息")

        # # 如果存在更新该MCP服务的状态
        app_config.mcp_config.mcpServers[server_name].enabled = enabled
        self.app_config_repository.save(app_config)
        return app_config.mcp_config
