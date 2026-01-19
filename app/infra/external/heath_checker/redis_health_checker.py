import logging

from app.domain.external.health_checker import HealthChecker
from app.domain.models.health_status import HealthStatus
from app.infra.storage.redis import RedisClient

logger = logging.getLogger(__name__)


class RegisHealthChecker(HealthChecker):
    """redis健康检查器"""

    def __init__(self, redis_client: RedisClient):
        self._redis_client = redis_client

    async def check(self) -> HealthStatus:
        try:
            if await self._redis_client.client.ping():
                return HealthStatus(
                    service="redis",
                    status="ok"
                )
            else:
                return HealthStatus(
                    service="redis",
                    status="error",
                    details="Redis Ping returned False"
                )
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return HealthStatus(
                service="redis",
                status="error",
                details=f"Exception: {str(e)}"
            )
