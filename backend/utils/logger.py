import sys
from pathlib import Path
from loguru import logger
from backend.config.settings import BASE_DIR, settings

# Ensure log directory exists
LOG_DIR = BASE_DIR / "backend" / "brain" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "jarvis.log"


def setup_logger():
    """Configures Loguru logger handlers with formatting and rotation."""
    logger.remove()

    # Console logging handler
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    log_level = "DEBUG" if settings.env == "development" else "INFO"

    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True
    )

    # File logging handler
    logger.add(
        str(LOG_FILE),
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        encoding="utf-8"
    )

    return logger


# Initialize on import
setup_logger()

__all__ = ["logger", "setup_logger"]
