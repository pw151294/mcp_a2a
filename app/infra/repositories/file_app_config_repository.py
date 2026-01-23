import logging
from pathlib import Path

import yaml
from filelock import FileLock

from app.domain.models.app_config import AppConfig, LLMConfig, AgentConfig, McpConfig
from app.domain.repositories.app_config_repository import AppConfigRepository

logger = logging.getLogger(__name__)


class FileAppConfigRepository(AppConfigRepository):
    """基于本地文件存储的应用配置仓库"""

    def __init__(self, config_path: str):
        """构造函数"""
        # 获取当前的项目的根目录
        root_dir = Path.cwd()

        # 拼接配置文件的路径并校验基础信息
        self._config_path = root_dir.joinpath(root_dir, config_path)
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_file = self._config_path.with_suffix(".lock")

    def _create_default_app_config_if_not_exists(self) -> None:
        """如果配置文件不存在则创建默认的配置文件"""
        if not self._config_path.exists():
            default_app_config = AppConfig(
                llm_config=LLMConfig(),
                agent_config=AgentConfig(),
                mcp_config=McpConfig()
            )
            self.save(default_app_config)

    def load(self) -> AppConfig:
        """从本地的yaml文件加载应用配置"""
        # 创建默认的配置文件（如果不存在的话）
        self._create_default_app_config_if_not_exists()

        try:
            # 打开配置文件并加载为AppConfig对象
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return AppConfig.model_validate(data) if data else None
        except Exception as e:
            logger.error(f"加载应用配置失败: {e}")
            raise RuntimeError("加载应用配置失败")

    def save(self, app_config) -> None:
        """将应用配置存储到本地的yaml文件中"""
        # 写入之前先上锁
        lock = FileLock(self._lock_file, timeout=5)

        try:
            with lock:
                # 将app_config转换为json
                app_config_json = app_config.model_dump(mode='json')

                # 打开配置文件并写入内容
                with open(self._config_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(app_config_json, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            logger.error(f"保存应用配置失败: {e}")
            raise RuntimeError("保存应用配置失败")
