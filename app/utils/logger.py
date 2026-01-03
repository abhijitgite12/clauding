"""Logging configuration for PySnagit."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(log_level=logging.DEBUG):
    """Set up application-wide logging with file and console handlers."""

    # Create logs directory
    log_dir = Path.home() / ".pysnagit" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file path
    log_file = log_dir / "pysnagit.log"

    # Create root logger
    logger = logging.getLogger("pysnagit")
    logger.setLevel(log_level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Log format
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )

    # Rotating file handler (5 MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Log startup
    logger.info("=" * 60)
    logger.info(f"PySnagit started at {datetime.now().isoformat()}")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 60)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(f"pysnagit.{name}")


# Create module-level loggers
class LoggerMixin:
    """Mixin class to add logging to any class."""

    @property
    def log(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
