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

class ListA2AServerItem(BaseModel):
    """A2A服务条目选项"""
    id: str = ""
    name: str = ""
    description: str = ""
    input_modes: List[str] = Field(default_factory=list)
    output_modes: List[str] = Field(default_factory=list)
    streaming: bool = True
    push_notifications: bool = False # 是否支持通知推送
    enabled: bool = True

class ListA2AServerResponse(BaseModel):
    """获取A2A服务列表响应结构"""
    a2a_servers: List[ListA2AServerItem] = Field(default_factory=list)