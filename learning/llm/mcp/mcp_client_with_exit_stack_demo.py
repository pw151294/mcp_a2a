import asyncio
import logging
from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.domain.models.search import SearchResults

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp.log"),
    ]
)
logger = logging.getLogger(__name__)


async def bing_search(query: str, date_range: Optional[str] = None):
    exit_stack = AsyncExitStack()

    try:
        transport = await exit_stack.enter_async_context(
            streamable_http_client("http://localhost:27017/bing_search/mcp"))
        read_stream, write_stream, _ = transport
        session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()
        # 调用bing搜索工具
        bing_search_response = await session.call_tool("bing_search", {"query": query, "date_range": date_range})
        logger.info(f"bing搜素工具调用结果：{bing_search_response}")
        # 解析出call tool result text
        contents = bing_search_response.content
        if len(contents) > 0:
            text = contents[0].text
            logger.info(f"call tool result text:{text}")
            search_results = SearchResults.model_validate_json(text)
            logger.info(f"bing search results:{search_results}")
    finally:
        await exit_stack.aclose()


async def main() -> None:
    exit_stack = AsyncExitStack()

    try:
        transport = await exit_stack.enter_async_context(streamable_http_client("http://localhost:9888/calculator/mcp"))
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
        call_tool_response = await session.call_tool("bash", {"command": "ls -la"})
        print("工具调用结果：", call_tool_response)
        call_tool_response = await session.call_tool("run_code",
                                                     {"language": "python", "code": "print('Hello from Python!')"})
        print("工具调用结果：", call_tool_response)
    finally:
        await exit_stack.aclose()


if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(bing_search(query="deepseek", date_range=None))
