from typing import Protocol, List, Dict, Any


class LLM(Protocol):
    """用于Agent应用和LLM进行交互的接口协议"""

    async def invoke(self,
                     message: List[Dict[str, Any]],
                     tools: List[Dict[str, Any]] = None,
                     response_format: Dict[str, Any] = None,
                     tool_choice: str = None
                     ) -> Dict[str, Any]:
        """传递消息列表、工具列表，响应格式和工具选择，调用语言模型并返回响应结果"""

        @property
        def model_name(self) -> str:
            """返回所使用的语言模型名称"""
            ...

        @property
        def temperature(self) -> float:
            """返回当前语言模型的温度设置"""
            ...

        @property
        def max_tokens(self) -> int:
            """返回当前语言模型的最大令牌数设置"""
            ...
