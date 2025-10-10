from multiprocessing import Lock
from typing import Any, Generator, List

from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._document import Document
from nre_pipeline.models._nlp_result import NLPResult, NLPResultItem
from nre_pipeline.processor._base import Processor


class NoOpProcessor(Processor):
    """A processor that performs no operations."""

    index = 1

    def _call(
        self, document_batch: DocumentBatch
    ) -> Generator[NLPResult, Any, None]:
        """Return the input document unchanged."""

        if not hasattr(self, "_lock"):
            self._lock = Lock()
        with self._lock:
            self.index += 1

        doc: Document
        for doc in document_batch:
            tokens: List[str] = doc.text.split()
            the_count = sum(1 for token in tokens if token.lower() == "the")
            fraction_of_thes = the_count / len(tokens) if len(tokens) > 0 else 0
            result = NLPResult(
                note_id=doc.note_id,
                results=[
                    NLPResultItem(key="first_word", value=doc.text.split()[0]),
                    NLPResultItem(key="last_word", value=doc.text.split()[-1]),
                    NLPResultItem(key="token_count", value=len(tokens)),
                    NLPResultItem(key="the_count", value=the_count),
                    NLPResultItem(key="fraction_of_thes", value=fraction_of_thes),
                ],
            )
            yield result
            self.index += 1
