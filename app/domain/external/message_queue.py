from typing import Protocol, Any, Tuple


class MessageQueue(Protocol):
    """消息队列协议 定义消息队列的基本操作接口"""

    async def put(self, message: Any) -> str:
        """将消息放入队列"""
        ...

    async def get(self, start_id: str = None, block_ms: int = None) -> Tuple[str, Any]:
        """根据传递的其实ID+阻塞时间获取一条数据"""
        ...

    async def pop(self) -> Tuple[str, Any]:
        """获取并移除消息队列中的第一条消息"""
        ...

    async def clear(self) -> None:
        """清空消息队列中的所有消息"""
        ...

    async def is_empty(self) -> bool:
        """检查消息队列是否为空"""
        ...

    async def size(self) -> int:
        """获取消息队列中的消息数量"""
        ...

    async def delete_message(self,message_id: str) -> bool:
        """删除指定ID的消息"""
        ...