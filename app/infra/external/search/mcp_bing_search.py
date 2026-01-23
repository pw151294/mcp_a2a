import logging
from typing import Optional

from mcp.server import FastMCP

from app.infra.external.search.bing_search import BingSearchEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp_bing_search.log"),
    ]
)

logger = logging.getLogger(__name__)

mcp = FastMCP()
mcp.settings.host = "localhost"
mcp.settings.port = 27017
mcp.settings.streamable_http_path = "/bing_search/mcp"

@mcp.tool()
async def bing_search(query: str, date_range: Optional[str] = None) -> dict:
    search_engine = BingSearchEngine()
    if date_range is None:
        date_range = "all"
    result = await search_engine.invoke(query, date_range)
    search_results = result.data
    return search_results.model_dump()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
