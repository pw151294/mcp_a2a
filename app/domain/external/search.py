from typing import Protocol, Optional

from app.domain.models.search import SearchResults
from app.domain.models.tool_result import ToolResult


class SearchEngine(Protocol):
    """搜索引擎API接口协议"""
    async def invoke(self,query: str,date_range:Optional[str] = None) -> ToolResult[SearchResults]:
        """根据传递的query+date_range时间筛选调用搜索引擎工具"""