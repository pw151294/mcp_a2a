import logging
from functools import lru_cache
from typing import Optional

from qcloud_cos import CosS3Client, CosConfig

from core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class Cos:
    """"腾讯云Cos对象存储"""

    def __init__(self):
        self._settings: Settings = get_settings()
        self._client: Optional[CosS3Client] = None

    async def init(self) -> None:
        """初始化Cos客户端"""
        # 1. 判断客户端是否存在 如果存在则记录日志并终止程序
        if self._client:
            logger.warning("Cos客户端已经存在 无需重复初始化")
            return

        try:
            config = CosConfig(
                Region=self._settings.cos_region,
                SecretId=self._settings.cos_secret_id,
                SecretKey=self._settings.cos_secret_key,
                Token=None,
                Scheme=self._settings.cos_scheme,
            )
            self._client = CosS3Client(config)
            logger.info("Cos客户端初始化成功")
        except Exception as e:
            logger.error("Cos客户端初始化失败: %s", e)

    async def shutdown(self) -> None:
        """关闭Cos客户端连接"""
        if self._client is not None:
            self._client = None
            logger.info("Cos客户端连接已关闭")

        get_cos.cache_clear()

    @property
    def client(self) -> CosS3Client:
        """只读属性 返回Cos客户端"""
        if self._client is None:
            raise RuntimeError("Cos客户端未初始化 请先调用init方法进行初始化")
        return self._client


@lru_cache
def get_cos() -> Cos:
    """使用lru_cache实现单例模式 获取Cos客户端单例对象"""
    return Cos()
