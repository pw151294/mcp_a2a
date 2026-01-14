import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main() -> None:
    exit_stack = AsyncExitStack()

    try:
        transport = await exit_stack.enter_async_context(streamable_http_client("http://localhost:8080/calculator/mcp"))
        rs, ws, _ = transport
        session = await exit_stack.enter_async_context(ClientSession(rs, ws))
        await session.initialize()
        # 获取工具列表信息
        list_tools_response = await session.list_tools()
        tools = list_tools_response.tools
        print("工具列表：", [tool.name for tool in tools])

        # 调用指定的工具
        call_tool_response = await session.call_tool("calculator", {"expression": "45**2 - 234/4.5"})
        print("工具调用结果：", call_tool_response)
    finally:
        await exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(main())
