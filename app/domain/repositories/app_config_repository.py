from typing import Protocol, Optional

from app.domain.models.app_config import AppConfig


class AppConfigRepository(Protocol):
    """应用配置仓库"""

    def load(self) -> Optional[AppConfig]:
        """加载应用配置"""
        ...

    def save(self, app_config: AppConfig) -> None:
        """保存应用配置"""
        ...
