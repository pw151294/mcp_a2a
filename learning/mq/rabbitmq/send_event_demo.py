import logging

from learning.mq.rabbitmq.producer_demo import UserServiceWithEvents
from learning.mq.rabbitmq.start_demo import queue_service

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rabbitmq.log'),
    ]
)

user_service = UserServiceWithEvents(queue_service)
user_service.create_user(1, "weipan4", "123456")
