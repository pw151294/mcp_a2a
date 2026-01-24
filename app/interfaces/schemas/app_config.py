from typing import List

from pydantic import BaseModel, Field

from app.domain.models.app_config import McpTransport


class ListMcpServerItem(BaseModel):
    """MCP服务列表条目选项"""
    server_name: str = ""  # 服务名称
    enabled: bool = True  # 启用状态
    transport: McpTransport = McpTransport.STREAMABLE_HTTP  # 传输协议
    tools: List[str] = Field(default_factory=list)  # 工具名字列表


class ListMcpServerResponse(BaseModel):
    """获取MCP服务列表"""
    mcp_servers: List[ListMcpServerItem] = Field(default_factory=list)  # MCP服务列表
