import json
import logging
import sys

import requests

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("error.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def http_post(url: str, params: dict, retry: int = 2, timeout: int = 5) -> dict | None:
    """post请求 支持重试 返回响应和json 失败返回None"""
    headers = {
        "workspace-id": "1",
        "Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxIiwiYWNjb3VudCI6ImFkbWluIiwiZXhwIjoxNzY4MzcyOTYzLCJpYXQiOjE3NjgzNjkzNjN9.tOJ1hhHHxhNnyBc5yvxbHQXZ0CphL9J2Gpt3Pzi2w8k"
    }
    for i in range(1, retry + 1):
        try:
            response = requests.post(url, headers=headers, json=json.dump(params, fp=sys.stdout))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            if i == retry:
                logger.error("请求超时，重试次数已用完: %s, Error: %s", url, str(e))
                break
            else:
                logger.warning("请求超时，正在重试第%d次: %s", i, url)
        except requests.exceptions.ConnectionError as e:
            logger.error("连接错误: %s, Error: %s", url, str(e))
            break
        except Exception as e:
            logger.error("请求异常: %s, Error: %s", url, str(e))
            break

    return None


if __name__ == "__main__":
    post_data = http_post("http://127.0.0.1:8000/login", {'name': 'weipan4'})
    logger.info("POST请求结果: %s", post_data)
