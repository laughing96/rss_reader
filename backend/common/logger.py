import logging
from logging.handlers import TimedRotatingFileHandler
import os

# 日志文件目录
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件路径
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def get_logger(name="my_logger", level=logging.INFO):
    """
    创建一个 logger
    :param name: logger 名称
    :param level: 日志级别
    :return: logging.Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 如果已经添加 handler，避免重复添加
    if logger.hasHandlers():
        return logger

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    # 文件 handler（按天轮转）
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # 添加 handler
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
logger = get_logger(name='rss_reader', level=logging.INFO)
