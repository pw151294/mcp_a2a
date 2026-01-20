from typing import List

from openai import BaseModel
from pydantic import Field


class Message(BaseModel):
    """"用户传递的消息"""
    message: str = ""  # 用户发送的消息
    attachments: List[str] = Field(default_factory=list)  # 用户发送的附件
