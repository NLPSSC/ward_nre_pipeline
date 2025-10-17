from dataclasses import dataclass, field
from tkinter import N
from typing import Any, List, Type, cast

from loguru import logger


@dataclass
class NLPResultItem:
    key: str
    value: Any
    value_type: Type | None = field(default=None)

    def __post_init__(self):
        if self.value_type is None:
            self.value_type = type(self.value)

    def __eq__(self, value: object) -> bool:
        lhs: NLPResultItem = cast(NLPResultItem, self)
        rhs: NLPResultItem = cast(NLPResultItem, value)
        keys_eq = lhs.key == rhs.key
        if keys_eq is False:
            logger.warning(f"Keys do not match: {lhs.key} != {rhs.key}")
            return False

        values_eq = lhs.value == rhs.value
        if values_eq is False:
            logger.warning(f"Values do not match: {lhs.value} != {rhs.value}")
            return False

        value_types_eq = lhs.value_type == rhs.value_type
        if value_types_eq is False:
            logger.warning(
                f"Value types do not match: {lhs.value_type} != {rhs.value_type}"
            )
            return False

        return keys_eq and values_eq and value_types_eq


@dataclass
class NLPResult:
    note_id: str | int
    results: List[NLPResultItem]

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, NLPResult):
            return False
        note_id_eq: bool = self.note_id == value.note_id
        if note_id_eq is False:
            logger.warning(f"Note IDs do not match: {self.note_id} != {value.note_id}")
            return False

        results_eq = self.results == value.results
        if results_eq is False:
            logger.warning(f"Results do not match: {self.results} != {value.results}")
            return False

        return note_id_eq and results_eq
    
    def __repr__(self):
        [r for r in self.results]
        return f"""
Note ID: {self.note_id}
Results: {self.results}
"""
