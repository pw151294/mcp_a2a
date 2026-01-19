from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """健康状态检查"""
    service: str = Field(default="", description="健康检查所对应的服务名称")
    status: str = Field(default="", description="健康检查状态，支持ok表示服务正常，error表示服务异常")
    details: str = Field(default="", description="健康检查的详细信息")
