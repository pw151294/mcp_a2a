from message_queue_demo import MessageQueueService


class UserServiceWithEvents:
    """用户服务 用作事件生产者"""

    def __init__(self, queue: MessageQueueService):
        self.queue = queue

    def create_user(self, user_id: int, username: str, password: str):
        """创建用户并发布用户创建事件"""
        user_dict = {
            "user_id": user_id,
            "username": username,
            "password": password,
        }
        self.queue.publish_message(routing_key="user.created", message=user_dict)
