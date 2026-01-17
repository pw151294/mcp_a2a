import logging
from functools import lru_cache

from app.domain.services.app_config_service import AppConfigService
from app.infra.repositories.file_app_config_repository import FileAppConfigRepository
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

