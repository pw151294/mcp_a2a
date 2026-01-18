from typing import Protocol

from app.domain.models.HealthStatus import HealthStatus


class HealthChecker(Protocol):
    """服务健康检查协议"""
    async def check(self) -> HealthStatus:
        """检查服务的健康状态"""
        ...