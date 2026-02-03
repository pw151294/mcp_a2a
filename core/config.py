from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MoocManus后端中控配置信息，从.env或者环境变量中加载数据"""
    # 项目基础配置
    env: str = "development"
    log_level: str = "INFO"
    app_config_path: str = "./config/config.yaml"

    # 数据库相关配置
    sqlalchemy_database_url: str = "postgresql+asyncpg://postgres:panwei960801@localhost:5432/manus"

    # redis缓存配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Cos腾讯云对象存储配置
    cos_secret_id: str = ""
    cos_secret_key: str = ""
    cos_region: str = ""
    cos_scheme: str = "https"
    cos_bucket: str = ""
    cos_domain: str = ""

    # sandbox沙箱配置
    sandbox_address: Optional[str] = None
    sandbox_image: Optional[str] = None
    sandbox_name_prefix: Optional[str] = None
    sandbox_ttl_minutes: Optional[int] = 60
    sandbox_network: Optional[str] = None
    sandbox_chrome_args: Optional[str] = None
    sandbox_https_proxy: Optional[str] = None
    sandbox_http_proxy: Optional[str] = None
    sandbox_no_proxy: Optional[str] = None

    # 使用pydantic v2的写法来实现环境变量信息的告知
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """获取当前项目的配置信息 并对内容进行缓存 避免重复读取"""
    settings = Settings()
    return settings
