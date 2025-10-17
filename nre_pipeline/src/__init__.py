"""
Non-Routine Events (NRE) Pipeline Package

This package provides tools and utilities for processing and analyzing
non-routine events in healthcare settings.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"


import sys
from loguru import logger
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def setup_logging(verbose: bool = False) -> None:
    if hasattr(setup_logging, "_setup_logging"):
        return

    """Set up logging configuration."""
    # Remove default handler
    logger.remove()

    # Add console handler with appropriate level
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sink=sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <cyan>{message}</cyan> | <level>{level}</level> | <magenta>{name}:{function}:{line}</magenta>",
        colorize=True,
        enqueue=True,
    )

    setattr(setup_logging, "_setup_logging", True)
