import asyncio
import logging
from typing import List, Dict, Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage
from pydantic import HttpUrl

from app.domain.external.llm import LLM
from app.domain.models.app_config import LLMConfig

logger = logging.getLogger(__name__)


class OpenAiLLM(LLM):
    """基于OpenAI语言模型的实现类"""

    def __init__(self, llm_config: LLMConfig) -> None:
        """构造函数，完成异步的openai客户端的创建和参数的初始化"""
        # 1.初始化异步客户端
        self._client = AsyncOpenAI(
            base_url=str(llm_config.base_url),
            api_key=llm_config.api_key,
        )

        # 2,完成其他参数的存储
        self._model_name = llm_config.model_name
        self._temperature = llm_config.temperature
        self._max_tokens = llm_config.max_tokens
        self._timeout = 3600  # 设置超时时间为3600秒

    @property
    def model_name(self) -> str:
        """返回所使用的语言模型名称"""
        return self._model_name

    @property
    def temperature(self) -> float:
        """返回当前语言模型的温度设置"""
        return self._temperature

    @property
    def max_tokens(self) -> int:
        """返回当前语言模型的最大令牌数设置"""
        ...
        return self._max_tokens

    async def invoke(self,
                     message: List[Dict[str, Any]],
                     tools: List[Dict[str, Any]] = None,
                     response_format: Dict[str, Any] = None,
                     tool_choice: str = None
                     ) -> Dict[str, Any]:
        """使用异步openapi客户端发起块响应（该步骤可以改成流式响应）"""
        try:
            # 检测是否传递了工具列表
            if tools:
                response = await self._client.chat.completions.create(
                    model=self._model_name,
                    messages=message,
                    temperature=self._temperature,
                    response_format=response_format,
                    tools=tools,
                    tool_choice=tool_choice,
                    parallel_tool_calls=False,
                    max_tokens=self._max_tokens,
                    timeout=self._timeout,
                )
            else:
                response = await self._client.chat.completions.create(
                    model=self._model_name,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    messages=message,
                    response_format=response_format,
                    timeout=self._timeout,
                )

            # 处理响应并返回结果
            logger.info(f"OpenAI语言模型调用成功: {response.model_dump(mode='json')}")
            return response.choices[0].message.model_dump()
        except Exception as e:
            logger.error(f"OpenAI语言模型调用失败: {e}")
            raise RuntimeError("OpenAI语言模型调用失败")


if __name__ == "__main__":
    async def main():
        llm = OpenAiLLM(LLMConfig(
            base_url=HttpUrl("https://api.deepseek.com"),
            api_key="sk-7755be2e4cd84360b9f731549dc093d4",
            model_name="deepseek-chat",
        ))
        response = await llm.invoke(
            [{"role": "user", "content": "Hello, world!"}],
        )
        print(response)
        response = ChatCompletionMessage.model_validate(response)
        print(response.model_dump_json())

    asyncio.run(main())
