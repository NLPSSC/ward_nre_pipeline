from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    note_id: str | int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
