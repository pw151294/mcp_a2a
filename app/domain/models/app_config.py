from pydantic import BaseModel, HttpUrl, Field


class LLMConfig(BaseModel):
    """语言模型配置"""
    base_url: HttpUrl = "https://api.deepseek.com"
    api_key: str = ""
    model_name: str = "deepseek-reasoner"  # 推理模型如果传递了tools的话会自动切换到deepseek-chat
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=8192,ge=0) # 最大输出的token数


class AppConfig(BaseModel):
    """应用配置信息 包括Agent配置、LLM提供商、A2A网络还有MCP服务等信息"""
    llm_config: LLMConfig