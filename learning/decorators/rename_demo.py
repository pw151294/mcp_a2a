import functools
import logging

from app.infra.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


# 使用装饰器之后 会导致__doc__还有__name__的名称被装饰器函数覆盖
def rename(func):
    def wrapper(*args, **kwargs):
        logger.info("begin function calling")
        func(*args, **kwargs)
        logger.info("end function calling")

    return wrapper

# 使用functools.wraps装饰器来保留原信息
def save_origin_name(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("begin function calling")
        func(*args, **kwargs)
        logger.info("end function calling")

    return wrapper


@rename
def say_hello():
    logger.info("hello world")


@save_origin_name
def say_goodbye():
    logger.info("goodbye world")


if __name__ == "__main__":
    print(say_hello.__name__)
    print(say_goodbye.__name__)
