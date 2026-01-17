import logging
import os

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("error.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def read_file(file_path: str, encoding: str = 'utf-8') -> str | None:
    """读取文件内容，返回字符串；失败返回空字符串并记录日志"""
    if not os.path.exists(file_path):
        logger.error("文件不存在: %s", file_path)
        return ""
    if os.path.isdir(file_path):
        logger.error("路径是一个目录，不是文件: %s", file_path)
        return ""

    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except PermissionError as e:
        logger.error("没有权限读取文件: %s, Error: %s", file_path, str(e))
        return ""
    except UnicodeDecodeError as e:
        logger.error("文件编码错误，尝试用gbk编码读取: %s, Error: %s", file_path, str(e))
        # 降级处理 尝试gbk编码
        try:
            with open(file_path, 'r', encoding='gbk') as file:
                return file.read()
        except Exception as e:
            logger.error("gbk编码读取失败: %s, Error: %s", file_path, str(e))
            return ""
    except Exception as e:
        logger.error("文件读取异常: %s, Error: %s", file_path, str(e))
        return ""


if __name__ == "__main__":
    print(read_file("./large_log.txt"))

    file_path = "/Users/panwei/Downloads/python/mcp+A2A/mcp_a2a/learning/file"
    print(os.getcwd())
    print(os.listdir(file_path))
    print(os.path.isfile(file_path))
    print(os.path.isdir(file_path))
    os.makedirs(file_path + "/test", exist_ok=True)
    print(os.listdir(file_path))
    os.remove(file_path + "/test")
    print(os.listdir(file_path))
