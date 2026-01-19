import logging
import queue
import random
import time
from threading import Thread

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("queue.log")
    ]
)
logger = logging.getLogger(__name__)


def producer(q: queue.Queue, n: int):
    for i in range(n):
        task = f"task-{i}"
        logger.info(f"producing task {task}")
        q.put(task)
        time.sleep(random.random())


def consumer(q: queue.Queue):
    while True:
        task = q.get()
        time.sleep(random.random())
        logger.info(f"consuming task {task}")
        q.task_done()


if __name__ == '__main__':
    q = queue.Queue()
    for i in range(10):
        thread = Thread(target=consumer, args=(q,), daemon=True)
        thread.start()
    producer(q, 10)
    q.join()
