from enum import Enum
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, HttpUrl, Field, ConfigDict, model_validator


class LLMConfig(BaseModel):
    """语言模型配置"""
    base_url: HttpUrl = "https://api.deepseek.com"
    api_key: str = ""
    model_name: str = "deepseek-reasoner"  # 推理模型如果传递了tools的话会自动切换到deepseek-chat
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=8192, ge=0)  # 最大输出的token数


class AgentConfig(BaseModel):
    """Agent通用配置"""
    max_iterations: int = Field(default=100, gt=0, lt=1000)  # 最大迭代次数
    max_retries: int = Field(default=3, gt=1, lt=10)  # 最大重试次数
    max_search_results: int = Field(default=10, gt=1, lt=30)  # 最大搜索结果数


class McpTransport(Enum):
    """MCP传输协议枚举"""
    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable_http"


class McpServerConfig(BaseModel):
    """MCP单条服务配置"""
    # 通过字段配置
    transport: McpTransport = McpTransport.STREAMABLE_HTTP  # 传输协议
    enabled: bool = True
    description: Optional[str] = None  # MCP服务描述
    env: Optional[Dict[str, Any]] = None  # 环境变量

    # stdio配置
    command: Optional[str] = None  # 启动命令
    args: Optional[List[str]] = None  # 启动参数

    # streamable_http和sse配置
    url: Optional[str] = None  # MCP服务的URL地址
    headers: Optional[Dict[str, Any]] = None  # headers请求头

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_mcp_server_config(self):
        """校验MCP服务配置的相关信息 包含URl+command"""
        # 1.将transport是否为sse/streamable_http
        if self.transport in [McpTransport.SSE, McpTransport.STREAMABLE_HTTP]:
            if not self.url:
                raise ValueError("在sse或者是streamable_http传输协议中必须传递URL")
        # 判断transport是否是stdio类型
        if self.transport == McpTransport.STDIO:
            if not self.command:
                raise ValueError("在stdio模式下必须传递command")

        return self


class McpConfig(BaseModel):
    """应用MCP配置"""
    mcpServers: Dict[str, McpServerConfig] = Field(default_factory=dict)  # mcp服务

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class AppConfig(BaseModel):
    """应用配置信息 包括Agent配置、LLM提供商、A2A网络还有MCP服务等信息"""
    llm_config: LLMConfig
    agent_config: AgentConfig  # 智能体通用的配置
    mcp_config: McpConfig  # MCP配置
