# 实现重试装饰器
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('info.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def retry(max_attempts: int, delay: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retry_times: int = 0
            while retry_times < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if retry_times == max_attempts - 1:
                        break
                    else:
                        retry_times += 1
                        time.sleep(delay)
                        logger.info(
                            f"Retrying {func.__name__}, attempt {retry_times + 1}/{max_attempts} after exception: {e}")
            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts.")
            raise RuntimeError(f"Function {func.__name__} failed after {max_attempts} attempts.")

        return wrapper

    return decorator
