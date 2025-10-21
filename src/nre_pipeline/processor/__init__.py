from typing import Literal, TypeAlias

from ._base_processor import Processor
from ._noop import NoOpProcessor


__all__ = [
    "Processor",
    "NoOpProcessor",
]
