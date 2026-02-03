import logging
from typing import Dict, Optional

from fastapi import APIRouter
from fastapi.params import Depends, Body

from app.application.services.app_config_service import AppConfigService
from app.domain.models.app_config import LLMConfig, AgentConfig, McpConfig, A2AServerConfig
from app.interfaces.schemas.app_config import ListMcpServerResponse, ListA2AServerResponse
from app.interfaces.schemas.base import Response
from app.interfaces.service_dependencies import get_app_config_service

logger = logging.getLogger(__name__)
app_config_router = APIRouter(prefix="/app_config", tags=["设置模块"])


@app_config_router.get(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="获取LLM配置信息",
    description="包括LLM提供的base_url、temperature、model_name还有max_tokens等信息"
)
async def get_llm_config(
        app_config_service: AppConfigService = Depends(get_app_config_service)  # 使用FASTAPI的Depends注入依赖
) -> Response[LLMConfig]:
    """获取LLM配置信息"""
    llm_config = await app_config_service.get_llm_config()
    return Response.success(data=llm_config.model_dump(exclude={"api_key"}))


@app_config_router.get(
    path="/agent",
    response_model=Response[AgentConfig],
    summary="获取Agent配置信息",
    description="包括最大迭代次数、最大重试次数、最大搜索结果数"
)
async def get_agent_config(
        app_config_service: AppConfigService = Depends(get_app_config_service)  # 使用FASTAPI的Depends注入依赖
) -> Response[AgentConfig]:
    """"""
    agent_config = await app_config_service.get_agent_config()
    return Response.success(data=agent_config.model_dump(exclude={"api_key"}))


@app_config_router.post(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="更新LLM配置信息",
    description="更新LLM配置信息，当api_key为空的时候表示不更新该字段"
)
async def update_llm_config(
        new_llm_config: LLMConfig,
        app_config_service: AppConfigService = Depends(get_app_config_service)
):
    """更新LLM配置信息"""
    update_llm_config = await app_config_service.update_llm_config(new_llm_config)
    return Response(
        msg="LLM配置信息更新成功",
        data=update_llm_config.model_dump(exclude={"api_key"}),
    )


@app_config_router.post(
    path="/agent",
    response_model=Response[AgentConfig],
    summary="更新Agent通用配置信息",
    description="更新Agent配置信息"
)
async def update_llm_config(
        new_agent_config: AgentConfig,
        app_config_service: AppConfigService = Depends(get_app_config_service)
):
    """更新LLM配置信息"""
    update_agent_config = await app_config_service.update_agent_config(new_agent_config)
    return Response(
        msg="AGent配置更新成功",
        data=update_agent_config.model_dump(),
    )


@app_config_router.get(
    path="/mcp-servers",
    response_model=Response[ListMcpServerResponse],
    summary="获取MCP服务器工具列表",
    description="获取当前系统的MC服务器列表，包含MCP服务名字、工具列表还有启用状态等"
)
async def get_mcp_servers(
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response:
    """获取当前系统的MCP服务器工具列表"""
    # todo 因为目前暂时未实现MCP客户端管理器 所以留到后面再实现
    mcp_servers = await app_config_service.get_mcp_servers()
    return Response.success(
        msg="获取MCP服务器列表成功",
        data=ListMcpServerResponse(mcp_servers=mcp_servers)
    )


@app_config_router.post(
    path="/mcp-servers",
    response_model=Response[Optional[Dict]],
    summary="新增MCP服务配置，支持传递一个或者多个配置",
    description="传递MCP配置信息为系统新增MCP工具"
)
async def create_mcp_servers(
        mcp_config: McpConfig,
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[Optional[Dict | str]]:
    """根据传递的配置信息创建MCP服务"""
    await app_config_service.update_and_create_mcp_config(mcp_config)
    return Response.success(msg="新增/更新配置成功")


@app_config_router.post(
    path="/mcp-servers/{server_name}/delete",
    response_model=Response[Optional[Dict]],
    summary="删除MCP服务配置",
    description="根据传递的MCP服务名字删除指定的MCP服务"
)
async def delete_mcp_server(
        server_name: str,
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[Optional[Dict | str]]:
    """根据服务名臣删除MCP服务配置"""
    await app_config_service.delete_mcp_server(server_name)
    return Response.success(msg="删除MCP配置成功")


@app_config_router.post(
    path="/mcp-servers/{server_name}/enables",
    response_model=Response[Optional[Dict]],
    summary="更新MCP服务的启用状态",
    description="根据传递的server_name+enabled更新指定的MCP服务的启用状态"
)
async def set_mcp_server_enabled(
        server_name: str,
        enabled: bool = Body(...),  # 说明是POST请求发送的请求体参数
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[Optional[Dict | str]]:
    """"根据传递的server_name+enabled更新服务的启用状态"""
    await app_config_service.set_mcp_server_enabled(server_name, enabled)
    return Response.success(msg="更新MCP启用状态成功")


@app_config_router.get(
    path="/a2a_servers",
    response_model=Response[ListA2AServerResponse],
    summary="获取a2a服务器列表",
    description="获取项目中所有已配置的a2a服务列表"
)
async def get_a2a_servers(
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response:
    """获取a2a服务列表"""
    a2a_servers = await app_config_service.get_a2a_server()
    return Response.success(
        msg="获取a2a服务列表成功",
        data=ListA2AServerResponse(a2a_servers=a2a_servers)
    )


@app_config_router.post(
    path="/a2a-servers/{a2a_id}/delete",
    response_model=Response[Optional[Dict]],
    summary="删除指定的a2a服务",
    description="根据A2A的服务标识删除指定的服务"
)
async def delete_a2a_server(
        a2a_id: str,
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[Optional[Dict]]:
    """根据ID删除a2a服务"""
    await app_config_service.delete_a2a_server(a2a_id)
    return Response.success(msg="删除a2a配置成功")


@app_config_router.post(
    path="/a2a-servers/{a2a_id}/enabled",
    response_model=Response[Optional[Dict]],
    summary="更新a2a服务的启用状态",
    description="根据ID更新a2a的启用状态"
)
async def set_a2a_enabled(
        a2a_id: str,
        enabled: bool = Body(embed=True),
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[Optional[Dict | str]]:
    """根据ID修改a2a服务的启用状态"""
    await app_config_service.set_a2a_server_enabled(a2a_id, enabled)
    return Response.success(msg="修改a2a服务启用状态成功")


@app_config_router.post(
    path="/a2a-servers/create",
    response_model=Response[Optional[Dict]],
    summary="创建a2a服务",
    description="创建新的A2A服务器配置"
)
async def create_a2a_server(
        base_url: str = Body(embed=True),
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[Optional[Dict | str]]:
    """创建新的a2a服务器配置"""
    await app_config_service.create_a2a_server(base_url)
    return Response.success(msg="创建a2a服务配置成功")
