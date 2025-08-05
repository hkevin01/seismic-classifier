"""Logging utilities for the seismic classifier."""

import logging
import sys
from pathlib import Path
from typing import Optional

from loguru import logger as loguru_logger


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger instance
    """
    # Configure loguru logger
    loguru_logger.remove()  # Remove default handler

    # Add console handler
    loguru_logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:"
        "<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
    )

    # Add file handler if logs directory exists
    logs_dir = Path("logs")
    if logs_dir.exists():
        loguru_logger.add(
            logs_dir / "seismic_classifier.log",
            rotation="1 day",
            retention="30 days",
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}",
        )

    # Create standard logger that forwards to loguru
    standard_logger = logging.getLogger(name)
    standard_logger.setLevel(getattr(logging, level.upper()))

    return standard_logger


def setup_logging(level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """Setup global logging configuration.

    Args:
        level: Logging level
        log_file: Optional log file path
    """
    loguru_logger.remove()

    # Console handler
    loguru_logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan> - <level>{message}</level>",
        level=level,
    )

    # File handler
    if log_file:
        loguru_logger.add(log_file, rotation="1 day", retention="30 days", level=level)
