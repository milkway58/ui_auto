"""
日志配置模块

提供统一的日志记录能力，输出到控制台和文件。
所有 BasePage 和业务模块通过 get_logger() 获取 logger 实例。

用法:
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("开始执行登录测试")
"""
import io
import logging
import sys
from pathlib import Path

from config.settings import settings


_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


def _setup_root_logger() -> None:
    """初始化根日志配置（仅执行一次）"""
    global _initialized
    if _initialized:
        return

    root = logging.getLogger("UI")
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root.setLevel(level)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # 控制台输出（UTF-8 编码，避免 Windows GBK 无法编码 ✓ 等 Unicode 符号）
    utf8_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    console_handler = logging.StreamHandler(utf8_stream)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    # 文件输出
    log_file = settings.log_path
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _initialized = True


def get_logger(name: str = "UI") -> logging.Logger:
    """
    获取指定名称的 logger

    Args:
        name: 模块名称，通常传 __name__

    Returns:
        logging.Logger 实例
    """
    _setup_root_logger()
    if not name.startswith("UI"):
        name = f"UI.{name}"
    return logging.getLogger(name)
