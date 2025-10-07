"""
Logging configuration for the KYC Document Processing API.
"""

import sys

from loguru import logger

from .config import settings


def setup_logging() -> None:
    """Configure application logging with loguru."""

    # Remove default handler
    logger.remove()

    # Add custom handler with structured format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console logging
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # File logging removed - using console/stdout only for direct execution


def get_logger(name: str):
    """Get a logger instance for a specific module."""
    return logger.bind(name=name)


class LoguruHandler:
    """Custom handler to integrate loguru with other logging systems."""

    def write(self, message: str) -> None:
        logger.opt(depth=6, exception=None).info(message.rstrip())

    def flush(self) -> None:
        pass
