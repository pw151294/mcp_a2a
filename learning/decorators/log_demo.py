import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('decorators.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_record(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Calling function '{func.__name__}' with args: {args} and kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"Function '{func.__name__}' returned: {result}")
        return result
    return wrapper