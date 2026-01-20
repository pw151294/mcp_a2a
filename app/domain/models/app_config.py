from pydantic import BaseModel, HttpUrl, Field


class LLMConfig(BaseModel):
    """语言模型配置"""
    base_url: HttpUrl = "https://api.deepseek.com"
    api_key: str = ""
    model_name: str = "deepseek-reasoner"  # 推理模型如果传递了tools的话会自动切换到deepseek-chat
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=8192, ge=0)  # 最大输出的token数


class AgentConfig(BaseModel):
    """Agent通用配置"""
    max_iterations: int = Field(default=100, gt=0, lt=1000)  # 最大迭代次数
    max_retries: int = Field(default=3, gt=1, lt=10)  # 最大重试次数
    max_search_results: int = Field(default=10, gt=1, lt=30)  # 最大搜索结果数


class AppConfig(BaseModel):
    """应用配置信息 包括Agent配置、LLM提供商、A2A网络还有MCP服务等信息"""
    llm_config: LLMConfig
    agent_config: AgentConfig # 智能体通用的配置
