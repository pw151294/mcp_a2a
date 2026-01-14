import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.infra.logging import setup_logging
from app.infra.storage.cos import get_cos
from app.infra.storage.postgres import get_postgres
from app.infra.storage.redis import get_redis
from app.interfaces.endpoints.routers import router
from core.config import get_settings
from contextlib import asynccontextmanager

# 1. 加载配置信息
settings = get_settings()

# 2. 初始化日志系统
setup_logging()
logger = logging.getLogger(__name__)

# 3. 定义FASTAPI的路由标签
openapi_tags = [
    {
        "name": "状态模块",
        "description": "包含 **状态检测** 等API接口，用于监测系统的运行状态"
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """创建FastAPI应用程序生命周期的上下文管理"""
    # 打印日志表示程序开始了
    logger.info("MoocManus后端服务正在启动...")

    # 初始化redis缓存客户端
    redis = get_redis()
    await redis.init()

    # 初始化postgres客户端
    postgres = get_postgres()
    await postgres.init()

    # 初始化腾讯云客户端
    cos = get_cos()
    await cos.init()

    try:
        # lifespan节点/分界
        yield
    finally:
        # 关闭redis缓存客户端
        await redis.shutdown()
        # 关闭postgres客户端
        await postgres.shutdown()
        logger.info("MoocManus后端服务正在关闭...")


app = FastAPI(
    title="MoocManus通用智能体",
    description="MoocManus是一个通用的AIAgent系统，可以完全私有化部署，使用A2A+MCP连接Agent/Tool，同时支持在沙箱环境中运行代码。",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
    version="0.1.0",
)

# 配置CORS中间件解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. 集成路由
app.include_router(router=router, prefix="/api")
