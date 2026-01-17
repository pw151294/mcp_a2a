import logging
from typing import Any

from learning.mq.rabbitmq.message_queue_demo import MessageQueueService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("rabbitmq.log"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


class OrderServiceWithEvents:
    """订单服务 事件消费者"""

    def __init__(self, queue: MessageQueueService):
        self.queue = queue

    def handle_user_created(self, user_data: dict[str, Any]):
        logger.info(f"订单服务收到用户创建事件：{user_data}")

    def start_consuming(self):
        self.queue.consume_message("user_created", callback=self.handle_user_created)
