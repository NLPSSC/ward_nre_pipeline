from multiprocessing import Lock
from typing import Any, Generator, List

from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._document import Document
from nre_pipeline.models._nlp_result_item import NLPResultFeature
from nre_pipeline.processor._base_processor import Processor


class NoOpProcessor(Processor):
    """A processor that performs no operations."""

    index = 1

    def _call_processor(
        self, document_batch: DocumentBatch
    ) -> Generator[NLPResultItem, Any, None]:
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
            result = NLPResultItem(
                note_id=doc.note_id,
                result_features=[
                    NLPResultFeature(key="first_word", value=doc.text.split()[0]),
                    NLPResultFeature(key="last_word", value=doc.text.split()[-1]),
                    NLPResultFeature(key="token_count", value=len(tokens)),
                    NLPResultFeature(key="the_count", value=the_count),
                    NLPResultFeature(key="fraction_of_thes", value=fraction_of_thes),
                ],
            )
            yield result
            self.index += 1
