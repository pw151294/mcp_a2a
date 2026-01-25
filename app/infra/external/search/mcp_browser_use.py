import asyncio

import dotenv
from browser_use import Agent, Browser, ChatBrowserUse

dotenv.load_dotenv()

async def example():
    # 初始化浏览器实例和LLM实例
    browser = Browser()
    llm = ChatBrowserUse()

    # 构建Browser智能体
    agent = Agent(
        task="帮我看下慕课网有哪些关于AI的体系课",
        llm=llm,
        browser=browser,
    )

    # 运行Agent并返回结果
    return await agent.run()

if __name__ == "__main__":
    history = asyncio.run(example())
    print(history)
