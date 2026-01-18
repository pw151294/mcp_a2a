import logging
from functools import lru_cache

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.app_config_service import AppConfigService
from app.application.services.status_service import StatusService
from app.infra.external.heath_checker.postgres_health_checker import PostgresHealthChecker
from app.infra.external.heath_checker.redis_health_checker import RegisHealthChecker
from app.infra.repositories.file_app_config_repository import FileAppConfigRepository
from app.infra.storage.postgres import get_db_session
from app.infra.storage.redis import RedisClient, get_redis
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache
def get_app_config_service() -> AppConfigService:
    """获取应用配置服务实例"""
    logger.info("加载获取AppConfigService应用配置服务实例")
    file_app_config_repository = FileAppConfigRepository(config_path=settings.app_config_path)

    # 实例化应用配置服务
    return AppConfigService(file_app_config_repository)


@lru_cache
def get_status_service(
        db_session: AsyncSession = Depends(get_db_session),
        redis_client: RedisClient = Depends(get_redis)
) -> StatusService:
    """获取状态服务实例"""
    # 1.初始化redis和postgres健康检查
    postgres_checker = PostgresHealthChecker(db_session)
    redis_checker = RegisHealthChecker(redis_client)

    # 2. 创建服务并返回
    logger.info("加载获取StatusService状态服务实例")
    return StatusService(
        checkers=[postgres_checker, redis_checker],
    )