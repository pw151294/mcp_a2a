import logging

from fastapi import APIRouter
from fastapi.params import Depends

from app.domain.models.app_config import LLMConfig, AgentConfig
from app.application.services.app_config_service import AppConfigService
from app.interfaces.service_dependencies import get_app_config_service
from app.interfaces.schemas.base import Response

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
