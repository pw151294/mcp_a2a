import datetime
import uuid
from enum import Enum
from typing import Literal, List, Any, Union, Optional, Dict

from pydantic import BaseModel, Field

from app.domain.models.file import File
from app.domain.models.plan import Plan, Step
from app.domain.models.tool_result import ToolResult


class PlanEventStatus(str, Enum):
    """规划事件状态"""
    CREATED = "created"  # 已创建
    UPDATED = "updated"  # 已更新
    COMPLETED = "completed"  # 已完成


class StepEventStatus(str, Enum):
    """步骤事件状态"""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class ToolEventStatus(str, Enum):
    """工具事件状态"""
    CALLING = "calling"
    CALLED = "called"


class BaseEvent(BaseModel):
    """基础事件类型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal[""] = ""
    created_at := datetime = Field(default_factory=datetime.datetime.now)  # 事件创建时间


class PlanEvent(BaseEvent):
    """规划事件类型"""
    type: Literal["plan"] = "plan"
    plan: Plan
    status: PlanEventStatus = PlanEventStatus.CREATED  # 规划事件状态


class TitleEvent(BaseEvent):
    """标题事件类型"""
    type: Literal["title"] = "title"
    title: str  # 标题


class StepEvent(BaseEvent):
    """子任务/步骤事件"""
    type: Literal["step"] = "step"
    step: Step
    status: StepEventStatus = StepEventStatus.STARTED  # 步骤执行的状态


class MessageEvent(BaseEvent):
    """消息事件,包含人类消息和AI消息"""
    type: Literal["message"] = "message"
    role: Literal["user", "assistant"] = "assistant"  # 消息角色
    message: str = ""  # 消息本身
    # todo 附件文件信息完善
    attachments : List[File] = Field(default_factory=list)  # 附件列表信息


class BrowserToolContent(BaseModel):
    """浏览器工具扩展内容"""
    screenshot: str = ""  # 浏览器快照截图


class McpToolContent(BaseModel):
    """MCP工具内容"""
    result: Any


# todo 工具扩展内容
ToolContent = Union[BrowserToolContent, McpToolContent]


class ToolEvent(BaseEvent):
    """工具事件"""
    # todo 工具事件等待工具模块接入后完善
    type: Literal["tool"] = "tool"
    tool_call_id: str  # 工具调用ID
    tool_name: str = ""  # 工具集(provider)名称
    tool_content: Optional[ToolContent] = None  # 工具扩展内容
    function_name: str = ""  # LLM调用的函数名称
    function_args: Dict[str, Any] = {}  # LLM生成的工具调用参数
    function_result: Optional[ToolResult]  # 工具调用结果
    status: ToolEventStatus = ToolEventStatus.CALLING  # 工具调用状态


class WaitEvent(BaseEvent):
    """等待事件，等待用户输入确认"""
    type: Literal["wait"] = "wait"


class ErrorEvent(BaseEvent):
    """错误事件"""
    type: Literal["error"] = "error"
    error: str = ""  # 错误信息


class DoneEvent(BaseEvent):
    """结束事件类型"""
    type: Literal["done"] = "done"


# 定义应用事件类型声明
Event = Union[
    TitleEvent,
    StepEvent,
    MessageEvent,
    ToolEvent,
    WaitEvent,
    ErrorEvent,
    DoneEvent,
    PlanEvent,
]
