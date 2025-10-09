from dataclasses import dataclass


@dataclass
class NLPResult:
    note_id: str | int
    results: dict[str, str]
