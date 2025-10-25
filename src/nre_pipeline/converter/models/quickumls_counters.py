from collections import Counter
from dataclasses import dataclass, field
from typing import Literal, Optional

from .consts import HeaderLabel, QuickUMLSField


@dataclass
class QuickUmlsCounter:
    field_counter: Counter = field(default_factory=Counter)

    def count(
        self, count_the: Literal["total_entries", "unique_entries", "unique_values"]
    ) -> int:
        if count_the == "total_entries":
            return sum(self.field_counter.values())
        elif count_the == "unique_entries":
            return len(self.field_counter)
        elif count_the == "unique_values":
            return len(set(self.field_counter.elements()))
        else:
            raise ValueError(f"Unknown count type: {count_the}")


@dataclass
class QuickUMLSCounters:
    cui_counter: QuickUmlsCounter = field(default_factory=QuickUmlsCounter)
    term_counter: QuickUmlsCounter = field(default_factory=QuickUmlsCounter)
    similarity_counter: QuickUmlsCounter = field(default_factory=QuickUmlsCounter)
    ngram_counter: QuickUmlsCounter = field(default_factory=QuickUmlsCounter)
    semantic_type_counter: QuickUmlsCounter = field(default_factory=QuickUmlsCounter)
    note_id_counter: QuickUmlsCounter = field(default_factory=QuickUmlsCounter)

    @classmethod
    def from_dict(cls, data: dict) -> "QuickUMLSCounters":
        instance = cls()
        for key, counter_data in data.items():
            if hasattr(instance, key):
                counter = QuickUmlsCounter()
                counter.field_counter = Counter(counter_data)
                setattr(instance, key, counter)
        return instance

    def _getitem(self, header_field: HeaderLabel) -> Optional[QuickUmlsCounter]:
        if hasattr(self, f"{header_field}_counter"):
            return getattr(self, f"{header_field}_counter")
        else:
            return None

    def increment(self, header_field: HeaderLabel, label: str, amount: int = 1):
        counter: Optional[QuickUmlsCounter] = self._getitem(header_field)
        if counter is not None:
            counter.field_counter.update({label: amount})
