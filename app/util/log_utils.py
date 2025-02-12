import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# 日志目录配置
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def configure_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """配置并返回一个日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 文件日志处理器（自动轮转）
    file_handler = RotatingFileHandler(
        LOG_DIR / "server.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(FORMATTER)

    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(FORMATTER)

    # 避免重复添加处理器
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# 全局日志实例
logger = configure_logger("mc-update-server")
