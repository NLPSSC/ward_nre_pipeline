from typing import TypeAlias, Union
from typing_extensions import Literal

NoteIdFeatureLabel: TypeAlias = Literal["note_id"]
DocumentFeature: TypeAlias = Union[NoteIdFeatureLabel, Literal["doc_length"]]
QuickUMLSField: TypeAlias = Literal["cui", "term", "similarity", "ngram", "semtypes"]
TokenFeature: TypeAlias = Literal["ngram", "pos_start", "pos_end"]
HeaderLabel: TypeAlias = Union[DocumentFeature, QuickUMLSField, TokenFeature]
