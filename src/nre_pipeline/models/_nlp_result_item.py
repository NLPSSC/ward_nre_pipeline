from dataclasses import dataclass, field
from typing import Any, Type, cast
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
