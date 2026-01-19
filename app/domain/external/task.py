from abc import ABC, abstractmethod
from typing import Protocol, Optional

from app.domain.external.message_queue import MessageQueue


class TaskRunner(ABC):
    """任务运行器 负责任务的执行 关心的是任务的执行、销毁还有释放资源"""
    @abstractmethod
    async def invoke(self, task: "Task") -> None:
        """调用任务并执行"""
        raise NotImplementedError

    @abstractmethod
    async def destroy(self) -> None:
        """销毁任务运行器 释放资源，包括：关闭网络连接、释放内训、清理临时内存还有清理后台资源"""
        raise NotImplementedError

    @abstractmethod
    async def on_done(self, task: "Task") -> None:
        """任务完成后的回调函数 可以用来处理任务完成后的清理工作"""
        raise NotImplementedError


class Task(Protocol):
    """定义任务相关的操作接口协议"""

    async def invoke(self) -> None:
        """运行任务的主要逻辑"""
        ...

    def cancel(self) -> bool:
        """取消任务的执行"""
        ...

    @property
    def input_stream(self) -> MessageQueue:
        """只读属性 返回任务的输入流"""
        ...

    @property
    def output_stream(self) -> MessageQueue:
        """只读属性 返回任务的输出流"""
        ...

    @property
    def id(self) -> str:
        """只读属性 返回任务的唯一标识符"""
        ...

    @property
    def done(self) -> bool:
        """只读属性 返回任务是否完成"""
        ...

    @classmethod
    def get(cls, task_id: str) -> Optional["Task"]:
        """根据任务ID获取任务实例"""
        ...

    @classmethod
    def create(cls, task_runner: TaskRunner) -> "Task":
        """创建一个新的任务实例并关联到指定的任务运行器"""
        ...

    @classmethod
    async def destroy(cls) -> None:
        """销毁任务实例 释放资源"""
        ...


