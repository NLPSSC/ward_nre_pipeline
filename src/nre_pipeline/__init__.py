"""
Non-Routine Events (NRE) Pipeline Package

This package provides tools and utilities for processing and analyzing
non-routine events in healthcare settings.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"


from loguru import logger


def setup_logging(verbose: bool = False) -> None:
    if hasattr(setup_logging, "_setup_logging"):
        return

    """Set up logging configuration."""
    # Remove default handler
    logger.remove()

    # Add console handler with appropriate level
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sink=lambda message: print(message, end=""),
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {message} | {level} | {name}:{function}:{line}",
        colorize=True,
        enqueue=True,
    )

    setattr(setup_logging, "_setup_logging", True)
