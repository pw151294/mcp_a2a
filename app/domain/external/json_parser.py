from typing import Protocol, Optional, Any, Union, Dict, List


class JsonParser(Protocol):
    """json解析器 用来解析json字符串并修复"""

    async def invoke(self, text: str, default_value: Optional[Any] = None) -> Union[Dict, List, Any]:
        """调用函数 用于将传递进来的文本进行解析"""
        ...
