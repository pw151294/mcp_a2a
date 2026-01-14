from typing import TypeVar, Generic, Optional

from pydantic import BaseModel, Field

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    """基础的API响应结构 继承BaseModel 并定义泛型"""
    code: int = 200  # 业务状态码 和http请求响应码保持一致
    msg: str = "success"  # 响应消息提示
    data: Optional[T] = Field(default_factory=dict)  # 响应数据 默认为空字典

    @staticmethod
    def success(data: Optional[T] = None, msg: str = "success") -> "Response[T]":
        """成功消息 传递data和msg"""
        return Response(code=200, msg=msg, data=data if data is not None else {})

    @staticmethod
    def fail(code: int, msg: str, data: Optional[T] = None) -> "Response[T]":
        """失败消息 传递code msg和data"""
        return Response(code=code, msg=msg, data=data if data is not None else {})

