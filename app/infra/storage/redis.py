import logging
from functools import lru_cache

from redis.asyncio import Redis

from core.config import get_settings, Settings

logger = logging.getLogger(__name__)


class RedisClient:
    """redis客户端 用于完成redis缓存的连接和使用"""

    def __init__(self):
        """构造函数 完成redis客户端的创建"""
        self._client: Redis | None = None
        self._settings: Settings = get_settings()

    async def init(self) -> None:
        """完成redis客户端的初始化"""
        # 1. 判断客户端是否存在 如果存在则表示已经连接上 无需重复连接
        if self._client:
            logger.warning("Redis客户端已经存在 无需重复初始化")
            return

        # 2. 创建redis客户端
        try:
            self._client = Redis(
                host=self._settings.redis_host,
                port=self._settings.redis_port,
                db=self._settings.redis_db,
                password=self._settings.redis_password,
                decode_responses=True
            )

            # 3. 测试连接redis缓存
            await self._client.ping()
            logger.info("Redis客户端初始化成功")
        except Exception as e:
            logger.error("Redis客户端初始化失败: %s", e)
            raise e

    async def shutdown(self) -> None:
        """关闭redis客户端连接"""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis客户端连接已关闭")

        # 2. 清除缓存
        get_redis.cache_clear()

    @property
    def client(self) -> Redis:
        """只读属性 返回redis客户端"""
        if self._client is None:
            raise RuntimeError("Redis客户端未初始化 请先调用init方法进行初始化")
        return self._client


@lru_cache
def get_redis() -> RedisClient:
    """使用lru_cache报实现单例模式 获取redis实例"""
    return RedisClient()
