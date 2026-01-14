from fastapi import APIRouter

from app.interfaces.endpoints.status_routers import status_router, logger


def create_api_routes() -> APIRouter:
    """创建API路由 涵盖整个项目的所有路由管理"""
    # 1. 创建APIRouter实例
    api_router = APIRouter()

    # 2. 将各个模块增加多api_router里面
    api_router.include_router(status_router)

    # 3. 返回api路由实例
    return api_router

router = create_api_routes()
