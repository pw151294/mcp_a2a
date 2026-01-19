from typing import Optional, TypeVar, Generic

from openai import BaseModel

T = TypeVar("T")

class ToolResult(BaseModel, Generic[T]):
    """工具执行结果"""
    success: bool = True # 工具是否成功调用
    message: Optional[str] = "" # 额外的信息提示
    data: Optional[T] = None # 工具的执行结果/数据
