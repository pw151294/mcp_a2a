import uuid
from enum import Enum
from typing import List, Any, Optional

from openai import BaseModel
from pydantic.v1 import Field


class ExecutionStatus(str, Enum):
    """规划/执行的状态"""
    PENDING = "PENDING"  # 空闲或者等待中
    RUNNING = "RUNNING"  # 执行中
    COMPLETED = "COMPLETED"  # 执行完成
    FAILED = "FAILED"  # 执行失败


class Step(BaseModel):
    """计划中的每一个步骤/子任务"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 子任务ID
    description: str = ""  # 步骤的描述信息
    status: ExecutionStatus = ExecutionStatus.PENDING  # 子任务的执行状态
    result: Optional[str] = None  # 执行结果
    error: Optional[str] = None
    success: bool = False  # 子任务是否执行成功
    attachments: List[str] = Field(default_factory=list)  # 附件列表信息

    @property
    def done(self) -> bool:
        """只读属性 返回步骤是否继续"""
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]


class Plan(BaseModel):
    """规划Domain模型 用来存储用户传递消息拆分出来的子任务/子步骤"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 计划ID
    title: str = ""  # 任务标题
    goal: str = ""  # 任务目标
    language: str = ""  # 工作语言
    steps: List[Any] = Field(default_factory=list)  # 步骤/子任务列表
    message: str = ""  # 用户传递的消息
    status: ExecutionStatus = ExecutionStatus.PENDING  # 规划的状态
    error: Optional[str] = None

    # todo 未预留result 用来记录规划的结果信息

    @property
    def done(self) -> bool:
        """只读属性 用来判断计划是否结束"""
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]

    def get_next_step(self) -> Optional[Step]:
        """获取需要执行的下一个步骤"""
        return next((step for step in self.steps if self.done), None)
