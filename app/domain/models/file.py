import uuid

from pydantic import BaseModel, Field


class File(BaseModel):
    """文件信息 记录Manus/Human上传的文件信息"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())) # 文件ID
    filename: str = "" # 文件名字
    filepath: str = "" # 文件路径
    key: str = "" # 腾讯云cos中的路径
    extension: str = "" # 文件扩展名
    mime_type: str = "" # mime-type类型
    size: int = 0 # 文件大小 单位为字节

