import asyncio
import uuid

import httpx


async def main() -> None:
    # 定义a2a远程agent-card的基础URL地址
    base_url = "http://127.0.0.1:9999"

    # 创建一个异步客户端上下文
    async with httpx.AsyncClient(timeout=6000) as httpx_client:
        # 获取Agent卡片信息
        agent_card_response = await httpx_client.get(f"{base_url}/.well-known/agent-card.json")
        agent_card_response.raise_for_status()
        print(f"Agent card response: {agent_card_response.json()}")

        # 提取Agent卡片的信息+请求端点
        agent_card = agent_card_response.json()
        url = agent_card.get("url", "")
        if not url:
            return

        # 构建发送消息请求体
        request_body = {
            "id": str(uuid.uuid4()),
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": uuid.uuid4().hex,
                    "role": "user",
                    "parts": [
                        {"kind": "text", "text": "帮我随机生成10个整数"}
                    ]
                }
            }
        }
        agent_response = await httpx_client.post(f"{url}", json=request_body)
        agent_response.raise_for_status()
        print(f"Agent response: {agent_response.json()}")

if __name__ == "__main__":
    asyncio.run(main())