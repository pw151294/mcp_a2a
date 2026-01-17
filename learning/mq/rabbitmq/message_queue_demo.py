import json
import logging

import pika
from pika.adapters.blocking_connection import BlockingChannel
from typing import Any, Callable  # added

from app.main import logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("rabbitmq.log"),
    ]
)


class MessageQueueService:
    """RabbitMq消息队列服务"""

    def __init__(self, host='localhost'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()
        # 声明交换机
        self.channel.exchange_declare(exchange='microservice', exchange_type='direct')
        self.channel.exchange_declare(exchange='order_created', exchange_type='direct')
        # 声明队列
        self.channel.queue_declare(queue='user_created')
        self.channel.queue_declare(queue='order_created')
        # 绑定队列到交换机
        self.channel.queue_bind(exchange='microservice', queue='user_created', routing_key='user.created')
        self.channel.queue_bind(exchange='order_created', queue='order_created', routing_key='order.created')

    def publish_message(self, routing_key: str, message: dict):
        """发布消息到指定路由键的队列"""
        self.channel.basic_publish(
            exchange='microservice',
            routing_key=routing_key,
            body=bytes(json.dumps(message).encode('utf-8')),
        )
        logging.info(f"Published message to {routing_key}: {message}")

    def consume_message(self, queue_name: str, callback: Callable[[dict[str, Any]], None]):
        """消费事件"""

        def message_handler(
                ch: BlockingChannel,
                method: pika.spec.Basic.Deliver,
                properties: pika.spec.BasicProperties,
                body: bytes
        ):
            data = json.loads(body.decode('utf-8'))
            logger.info(f"Received message: {data}")
            callback(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)


        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=message_handler
        )
        self.channel.start_consuming()
