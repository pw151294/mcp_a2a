import logging
import sys

from core.config import get_settings


def setup_logging():
    """配置MoocManus项目的日志系统 涵盖日志等级 输出格式 输出渠道等"""
    # 获取项目配置
    settings = get_settings()

    # 获取根日志处理器
    root_logger = logging.getLogger()

    # 设置根日志处理等级
    log_level = getattr(logging, settings.log_level)
    root_logger.setLevel(log_level)

    # 日志输出格式
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 创建控制台日志输出处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # 将控制台日志处理器添加到根日志处理器中
    root_logger.addHandler(console_handler)
    root_logger.info("日志系统已初始化，当前日志等级为: %s", settings.log_level)