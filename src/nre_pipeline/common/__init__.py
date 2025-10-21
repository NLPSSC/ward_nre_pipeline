import sys
from loguru import logger


def setup_logging(*, verbose: bool = False):
    """Set up logging configuration."""
    if hasattr(setup_logging, "_setup_logging") is False:
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

    return logger
