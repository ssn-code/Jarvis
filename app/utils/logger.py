import sys
import logging
from pathlib import Path
from loguru import logger
from app.config import settings

def get_logs_dir() -> Path:
    """Returns the logs directory path dynamically based on settings."""
    return settings.db.sqlite_db_path.parent / "logs"


def get_log_file() -> Path:
    """Returns the log file path dynamically based on settings."""
    return get_logs_dir() / "jarvis.log"


class InterceptHandler(logging.Handler):
    """
    Intercepts standard library logging messages and forwards them to Loguru.
    Based on standard recipe in Loguru documentation:
    https://loguru.readthedocs.io/en/stable/resources/recipes.html#intercepting-standard-logging-messages-while-using-loguru-sink
    """
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logged message originated
        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """Configures system-wide logging using loguru with file and console sinks."""
    logs_dir = get_logs_dir()
    log_file = get_log_file()

    # Ensure logs directory exists
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Remove all default handlers to avoid duplicate output
    logger.remove()

    # Determine console logging level based on application environment
    console_level = "INFO" if settings.env == "production" else "DEBUG"

    # Add console sink
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=console_level,
        enqueue=True,
        backtrace=True,
        diagnose=settings.env != "production"
    )

    # Add rotating log file sink
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="00:00",  # Daily at midnight
        retention="30 days",  # Retain logs for 30 days
        compression="zip",  # Zip compressed log archives
        enqueue=True,
        backtrace=True,
        diagnose=settings.env != "production"
    )

    # Set up root logger with InterceptHandler to capture logs from standard library
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Route major third-party library loggers into our system-wide logging
    for logger_name in ["uvicorn", "uvicorn.access", "fastapi", "httpx", "chromadb", "apscheduler"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = []
        logging_logger.propagate = True

    logger.info("System-wide logging initialized successfully.")
