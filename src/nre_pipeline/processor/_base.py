from abc import ABC
from typing import Any, Generator

from nre_pipeline.models import NLPResult
from nre_pipeline.models._batch import DocumentBatch


class Processor(ABC):
    def __init__(self, processor_id: int) -> None:
        super().__init__()
        self._index = processor_id

    def __call__(
        self, document_batch: DocumentBatch
    ) -> Generator[NLPResult, Any, None]:
        """Process a document and return the result."""
        raise NotImplementedError("Subclasses must implement this method.")
