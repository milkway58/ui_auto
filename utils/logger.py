"""
日志配置模块

提供统一的日志记录能力，输出到控制台和文件。
所有 BasePage 和业务模块通过 get_logger() 获取 logger 实例。
每次执行生成独立日志文件，文件名格式：YYYY-MM-DD_HH-MM-SS.log

用法:
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("开始执行登录测试")
"""
import io
import logging
import sys
from datetime import datetime
from pathlib import Path

from config.settings import settings

# 日志目录
_LOG_DIR: Path = Path(__file__).resolve().parent.parent / "reports" / "logs"

# 控制台：简洁格式（仅时间 + 级别 + 消息）
_CONSOLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
# 文件：完整格式（含模块/文件名/行号）
_FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


def _setup_root_logger() -> None:
    """初始化根日志配置（仅执行一次），每次进程启动生成新的时间戳日志文件"""
    global _initialized
    if _initialized:
        return

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("UI")
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root.setLevel(level)

    console_formatter = logging.Formatter(_CONSOLE_FORMAT, datefmt=_DATE_FORMAT)
    file_formatter = logging.Formatter(_FILE_FORMAT, datefmt=_DATE_FORMAT)

    # 控制台输出（简洁格式，UTF-8 编码）
    utf8_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    console_handler = logging.StreamHandler(utf8_stream)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    # 文件输出（完整格式，每次执行独立文件）
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = _LOG_DIR / f"{timestamp}.log"
    file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root.addHandler(file_handler)

    # 首行记录日志文件路径
    root.info(f"日志文件: {log_file}")

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
