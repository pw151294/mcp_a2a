from app.domain.models.app_config import LLMConfig, AppConfig
from app.domain.repositories.app_config_repository import AppConfigRepository


class AppConfigService:
    def __init__(self, app_config_repository: AppConfigRepository) -> None:
        """构造函数 完成依赖注入"""
        self.app_config_repository = app_config_repository

    def _load_app_config(self) -> AppConfig:
        """加载获取所有的应用配置信息"""
        return self.app_config_repository.load()

    def get_llm_config(self) -> LLMConfig:
        """加载LLM提供商配置信息"""
        return self._load_app_config().llm_config

    def update_llm_config(self, llm_config: LLMConfig) -> LLMConfig:
        """根据传递的llm_config更新语言模型的供应商配置"""
        # 获取应用配置
        app_config = self._load_app_config()

        # 判断api_key是否为空
        if not llm_config.api_key.strip():
            llm_config.api_key = app_config.llm_config.api_key

        # 调用函数更新app_config
        app_config.llm_config = llm_config
        self.app_config_repository.save(app_config)

        return app_config.llm_config
