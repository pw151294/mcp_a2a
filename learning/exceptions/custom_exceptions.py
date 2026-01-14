import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("error.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class UserExistsError(Exception):
    """自定义异常 表示用户已存在"""
    pass


class PasswordTooShortError(Exception):
    """自定义异常 表示密码长度过短"""

    def __init__(self, length: int, min_length: int):
        self.length = length
        self.min_length = min_length
        super().__init__(f"密码长度{length}，至少需{min_length}位")


def create_user(username: str, password: str):
    """创建用户 校验用户名重复还有密码长度"""
    if username in ['admin']:
        raise UserExistsError
    elif len(password) < 8:
        raise PasswordTooShortError(len(password), 8)


# 测试代码
if __name__ == "__main__":
    try:
        create_user(username="weipan4", password="12345")
    except (UserExistsError, PasswordTooShortError) as e:
        logger.error("创建用户失败: %s", e)
