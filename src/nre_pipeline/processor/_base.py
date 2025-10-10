from abc import ABC, abstractmethod
import queue
from typing import Any, Generator

from nre_pipeline.models import NLPResult
from nre_pipeline.models._batch import DocumentBatch
import threading


class Processor(ABC):
    def __init__(self, processor_id: int) -> None:
        super().__init__()
        self._index = processor_id
        self._queue: queue.Queue

    def __call__(self, document_batch: DocumentBatch):
        """Process a document and return the result."""
        # Add the processing task to the queue as a thread

        def task():
            for result in self._call(document_batch):
                self._queue.put(result)

        thread = threading.Thread(target=task)
        thread.start()

    @abstractmethod
    def _call(self, document_batch: DocumentBatch) -> Generator[NLPResult, Any, None]:
        """Process a document and return the result."""
        raise NotImplementedError("Subclasses must implement this method.")
