import logging
import threading

from learning.mq.rabbitmq.consumer_demo import OrderServiceWithEvents
from learning.mq.rabbitmq.message_queue_demo import MessageQueueService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("rabbitmq.log"),
    ]
)

queue_service = MessageQueueService()

def init():
    order_service = OrderServiceWithEvents(queue_service)

    # 启动消费者线程
    consumer_thread = threading.Thread(target=order_service.start_consuming)
    consumer_thread.daemon = True
    consumer_thread.start()
    logging.info("consumer thread started")

    # 阻塞主线程，防止程序退出
    try:
        while True:
            pass  # 或者使用 time.sleep(1) 让主线程保持运行
    except KeyboardInterrupt:
        logging.info("程序已终止")

if __name__ == '__main__':
    init()