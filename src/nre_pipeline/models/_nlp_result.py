from dataclasses import dataclass
from typing import Any, List, Type


@dataclass
class NLPResultItem:
    key: str
    value: Any
    value_type: Type


@dataclass
class NLPResult:
    note_id: str | int
    results: List[NLPResultItem]
