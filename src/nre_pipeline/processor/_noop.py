from multiprocessing import Lock

from nre_pipeline.models._document import Document
from nre_pipeline.models._nlp_result import NLPResult
from nre_pipeline.processor._base import Processor


class NoOpProcessor(Processor):
    """A processor that performs no operations."""

    index = 1

    def __call__(self, document: Document) -> NLPResult:
        """Return the input document unchanged."""
        result = NLPResult(note_id=self.index, results={})

        if not hasattr(self, "_lock"):
            self._lock = Lock()
        with self._lock:
            self.index += 1
        return result
        return result
