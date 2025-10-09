from abc import ABC

from nre_pipeline.models import NLPResult
from nre_pipeline.models._batch import DocumentBatch


class Processor(ABC):
    def __init__(self, index: int) -> None:
        super().__init__()
        self._index = index

    def __call__(self, document_batch: DocumentBatch) -> NLPResult:
        """Process a document and return the result."""
        raise NotImplementedError("Subclasses must implement this method.")
