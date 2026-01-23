from typing import Optional, List

from openai import BaseModel
from pydantic import Field


class SearchResultItem(BaseModel):
    """搜索条目数据类型"""
    url: str # 搜索条目的URL链接
    title: str  # 搜索条目标题
    snippet: str # 搜索条目摘要信息

class SearchResults(BaseModel):
    """搜索结果"""
    query: str # 查询query
    date_range: Optional[str] = None # 日期范围
    total_results: int = 0 # 搜索结果条数
    results: List[SearchResultItem] = Field(default_factory=list) # 搜索结果
