import logging

from fastapi import APIRouter

from app.interfaces.schemas import Response

logger = logging.getLogger(__name__)
status_router = APIRouter(prefix="/status", tags=["status"])

@status_router.get(path="",
                   response_model=Response,
                   summary="系统健康检查",
                   description="检查系统的postgres、redis还有fastapi等组件的状态信息")
async def get_status() -> Response:
    """系统健康检查 检查postgres/redis/fastapi/cos等服务"""
    # todo 等待postgres/redis/cos/等服务接入之后补全代码
    return Response.success()
