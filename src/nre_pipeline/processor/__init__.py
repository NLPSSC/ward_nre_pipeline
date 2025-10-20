from typing import Literal, TypeAlias

from ._base import Processor
from ._noop import NoOpProcessor


__all__ = [
    "Processor",
    "NoOpProcessor",
]
