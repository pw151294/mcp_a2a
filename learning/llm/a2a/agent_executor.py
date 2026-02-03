import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.utils import new_agent_text_message
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam


class DeepSeekAgent:
    @classmethod
    async def invoke(cls, query: str) -> str:
        client = AsyncOpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key="sk-lzzrulgfvlbykywprnohfegfenxeabzwehjktfitkyeyhcdp"
        )
        messages: list[ChatCompletionSystemMessageParam | dict] = [
            {"role": "user", "content": query}
        ]
        response = await client.chat.completions.create(
            model="Qwen/Qwen3-Next-80B-A3B-Instruct",
            messages=messages
        )
        return f"回复内容：{response.choices[0].message.content}"


class DeepSeekAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = DeepSeekAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.message.parts[0].root.text
        answer = await self.agent.invoke(query)
        await event_queue.enqueue_event(new_agent_text_message(answer))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("不支持取消")


if __name__ == "__main__":
    # 定义技能
    skill = AgentSkill(
        id="calculator",
        name="计算器",
        description="真实计算各类复杂数学公式",
        tags=["计算器"],
        examples=["445*34", "211/34.2+12"]
    )

    # 定义agent卡片
    agent_card = AgentCard(
        name="DeepSeek智能体",
        description="这是可以调用deepseek模型进行深度思考的智能体，在需要深度思考的时候可以使用",
        url="http://localhost:9999",
        version="0.0.1",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supports_authenticated_extended_card=False
    )

    # 使用A2A默认的请求处理器（jsonrpc）
    request_handler = DefaultRequestHandler(
        agent_executor=DeepSeekAgentExecutor(),
        task_store=InMemoryTaskStore()
    )

    # 创建/启动A2A服务器
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    uvicorn.run(server.build(), host="0.0.0.0", port=9999)
