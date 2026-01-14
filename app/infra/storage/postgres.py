import logging
from functools import lru_cache
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import text
from core.config import get_settings

logger = logging.getLogger(__name__)


class Postgres:
    """Postgres数据库基础类 用于完成数据库连接等配置操作"""

    def __init__(self):
        """构造函数 完成postgres数据库引擎还有会话工厂的建立"""
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._settings = get_settings()

    async def init(self):
        """初始化postgres连接"""
        if self._engine is not None:
            logger.warning("Postgres数据库引擎已经存在 无需重复初始化")
            return

        try:
            # 创建异步引擎
            self._engine = create_async_engine(
                self._settings.sqlalchemy_database_url,
                echo=True if self._settings.env == "development" else False,
            )

            # 创建会话工厂
            self._session_factory = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            logger.info("Postgres数据库会话工厂成功")

            # 连接postgres并执行预操作
            async with self._engine.begin() as async_conn:
                # 检查是否安装了uuid扩展 如果没有安装则进行安装
                await async_conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
                logger.info("Postgres数据库引擎初始化成功")

        except Exception as e:
            logger.error("Postgres数据库引擎初始化失败: %s", e)
            raise e

    async def shutdown(self) -> None:
        """关闭Postgres数据库连接"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Postgres数据库连接已关闭")
        get_postgres.cache_clear()

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """只读属性 返回已初始化的会话工厂"""
        if self._session_factory is None:
            raise RuntimeError("Postgres数据库会话工厂未初始化 请先调用init方法进行初始化")
        return self._session_factory

@lru_cache
def get_postgres() -> Postgres:
    """使用lru_cache实现单例模式 获取Postgres数据库实例"""
    return Postgres()

async def get_db_session() -> AsyncSession:
    """FASTAPI依赖项 用来在每个请求中异步获取数据库会话实例 确保会话在正确使用之后被关闭"""
    # 1. 获取引擎和会话工厂
    db = get_postgres()
    session_factory = db.session_factory

    # 2. 创建会话上下文 在上下文内完成数据提交
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
