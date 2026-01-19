import asyncio
import logging

from pydantic import HttpUrl

from app.domain.models.app_config import LLMConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("decorators.log")
    ]
)
logger = logging.getLogger(__name__)


class LLMConfigValidator:
    def __init__(self, func):
        self.func = func

    async def __call__(self, *args, **kwargs):
        if not isinstance(args[0], LLMConfig):
            raise ValueError(f"参数类型不匹配：{type(args[0])}")
        llm_config: LLMConfig = args[0]
        if not llm_config.base_url:
            raise ValueError("base url can not be empty")
        if not llm_config.api_key:
            raise ValueError("api key can not be empty")
        if not llm_config.model_name:
            raise ValueError("model name can not be empty")
        if not llm_config.temperature or llm_config.temperature <= 0:
            raise ValueError("temperature can not be negative")
        if not llm_config.max_tokens or llm_config.max_tokens <= 0:
            raise ValueError("max_tokens can not be negative")
        result = await self.func(*args, **kwargs)
        return result


@LLMConfigValidator
async def save_llm_config(llm_config: LLMConfig):
    logger.info("save llm config success")


if __name__ == "__main__":
    llm_config = LLMConfig(
        base_url=HttpUrl("http://127.0.0.1:5000"),
        api_key="123456",
        model_name="deepseek-chat",
        temperature=0,
        max_tokens=0
    )
    try:
        asyncio.run(save_llm_config(llm_config))
    except ValueError as e:
        logger.error(f"save llm config failed: {str(e)}")
