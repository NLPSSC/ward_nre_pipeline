from dataclasses import dataclass, field


@dataclass
class Document:
    note_id: str | int
    text: str
    metadata: dict[str, str] = field(default_factory=dict)
