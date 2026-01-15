import logging

from pydantic.v1 import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('info.log'),
        logging.StreamHandler()
    ]
)


class UserInfo(BaseModel):
    username: str = None
    password: str = None
    email: str = None


def validate_input(func):
    def wrapper(*args, **kwargs):
        # 1. args为空则跳过校验，如果非空，所有参数必须都是整数类型
        if args and not all(isinstance(arg, int) for arg in args):
            error_msg = "Invalid positional arguments. All positional arguments must be integers."
            logging.error(error_msg)
            raise ValueError(error_msg)

        # 2. kwargs如果为空则跳过检验，如果非空，所有值必须都是字符串类型
        if kwargs and not all(isinstance(value, str) for value in kwargs.values()):
            error_msg = "Invalid keyword arguments. All keyword argument values must be strings."
            logging.error(error_msg)
            raise ValueError(error_msg)

        return func(*args, **kwargs)

    return wrapper


def validate_output(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # 对输出的校验逻辑
        if not isinstance(result, UserInfo):
            error_msg = "Invalid output data. The result must be an instance of UserInfo."
            logging.error(error_msg)
            raise ValueError(error_msg)
        return result

    return wrapper
