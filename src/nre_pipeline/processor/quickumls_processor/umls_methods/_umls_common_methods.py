from dataclasses import dataclass
from typing import List


@dataclass
class _UMLSCui:
    cui: str
    term: str


@dataclass
class UMLSTerm(_UMLSCui):
    source_vocabulary: str


@dataclass
class UMLSSemanticType(_UMLSCui):
    semantic_types: List[str]
