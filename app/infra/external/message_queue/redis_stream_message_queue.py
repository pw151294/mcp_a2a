import asyncio
import json
import logging
import uuid
from typing import Tuple, Any, Optional

from app.domain.external.message_queue import MessageQueue
from app.infra.storage.redis import get_redis

logger = logging.getLogger(__name__)


class RedisStreamMessageQueue(MessageQueue):
    """基于redis stream的消息队列实现"""

    def __init__(self, stream_name: str) -> None:
        """构造函数，完成redis stream的初始化 包含锁的名字"""
        self._stream_name = stream_name
        self._redis_client = get_redis()
        self._lock_expire_seconds = 10

    async def put(self, message: Any) -> str:
        """将消息放入队列并返回消息ID"""
        logger.info(f"Putting message: {message}")
        return await self._redis_client.client.xadd(self._stream_name, {"data": message})

    async def pop(self) -> Tuple[str, Any]:
        """从队列中弹出一条消息并返回消息ID和消息内容"""
        logger.info(f"从消息队列弹出消息: {self._stream_name}")
        lock_key = f"lock:{self._stream_name}:pop"

        # 构建分布式锁 如果分布式锁创建失败就返回None
        lock_val = await self._acquire_lock(lock_key, timeout_seconds=self._lock_expire_seconds)
        if not lock_val:
            logger.info(f"获取分布式锁失败，无法弹出消息: {self._stream_name}")
            return None, None

        try:
            # 从redis stream内获取一条数据
            messages = await self._redis_client.client.xrange(self._stream_name, "-", "+", count=1)
            if not messages:
                return None, None
            else:
                # 从消息列表里取出对应的消息数据
                message_id, message_data = messages[0]
                # 删除该消息
                await self._redis_client.client.xdel(self._stream_name, message_id)
                return message_id, message_data["data"]
        except Exception as e:
            logger.error(f"从消息队列弹出消息失败: {e}")
            return None, None
        finally:
            # 释放分布式锁
            await self._release_lock(lock_key, lock_val)

    async def get(self, start_id: str = None, block_ms: int = None) -> Tuple[str, Any]:
        """从队列中获取一条消息但不删除它，返回消息ID和消息内容"""
        logger.info(f"Getting message from stream: {self._stream_name}")

        # 1. 判断start_id是否为None
        if start_id is None:
            start_id = "0"

        # 2. 从redis stream内获取一条数据
        messages = await self._redis_client.client.xread(
            {self._stream_name: start_id},
            count=1,
            block=block_ms
        )

        # 3. 检查message是否存在
        if not messages:
            return None, None

        # 4. 从消息列表里取出对应的消息数据
        stream_messages = messages[0][1][0]
        if not stream_messages:
            return None, None

        # 5. 提取ID和数据
        message_id, message_data = stream_messages

        # 返回ID和数据
        try:
            return message_id, message_data.get("data")
        except Exception as e:
            logger.error(f"从消息队列获取消息失败: {e}")
            return None, None

    async def clear(self) -> None:
        """清空消息队列中的所有消息"""
        await self._redis_client.client.xtrim(self._stream_name, 0)

    async def is_empty(self) -> bool:
        """检查消息队列是否为空"""
        return self.size() == 0

    async def size(self) -> int:
        """获取消息队列中的消息数量"""
        return await self._redis_client.client.xlen(self._stream_name)

    async def delete_message(self, message_id: str) -> bool:
        """删除指定ID的消息"""
        try:
            await self._redis_client.client.xdel(self._stream_name, message_id)
            return True
        except Exception as e:
            logger.error(f"删除消息失败: {e}")
            return False

    async def _acquire_lock(self, lock_key: str, timeout_seconds: int) -> Optional[str]:
        """根据传递的lock建构建一个分布式锁"""
        # 1. 创建锁对应的值
        lock_val = str(uuid.uuid4())
        end_time = timeout_seconds

        # 2. 使用end_time构建循环
        while end_time > 0:
            # 3. 使用redis的set方法 将lock_key还有lock_val存入redis内，并设置过期时间
            result = await self._redis_client.client.set(
                lock_key,
                lock_val,
                nx=True,  # 如果不存在则设置
                ex=self._lock_expire_seconds,
            )

            # 4. 如果设置成功 就返回锁的值
            if result:
                return lock_val

            # 5. 睡眠指定时间 并将end_time减少
            await asyncio.sleep(0.1)
            end_time -= 0.1

        return None

    async def _release_lock(self, lock_key: str, lock_val: str) -> bool:
        """释放分布式锁"""
        # 1. 构建一段redis的脚本释放分布式锁
        release_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """

        # 2. 执行脚本
        try:
            # 注册脚本
            script = self._redis_client.client.register_script(release_script)
            # 执行脚本并传递keys+args释放分布式锁
            result = await script(keys=[lock_key], args=[lock_val])
            return result == 1
        except Exception as e:
            logger.error(f"释放分布式锁失败: {e}")
            return False


if __name__ == "__main__":
    redis = get_redis()
    asyncio.run(redis.init())
    message_queue = RedisStreamMessageQueue("test")

    user1 = {"name": "Alice", "age": 30}
    user2 = {"name": "Bob", "age": 35}

    asyncio.run(message_queue.put(json.dumps(user1)))
    asyncio.run(message_queue.put(json.dumps(user2)))

    message_id, message_data = asyncio.run(message_queue.get())
    print(message_id, message_data)

    pop_id, pop_data = asyncio.run(message_queue.pop())
    print(pop_id, message_data)
