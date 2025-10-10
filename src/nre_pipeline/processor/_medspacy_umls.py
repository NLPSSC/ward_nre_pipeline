import os
from pathlib import Path
from typing import Any, Generator, List

import medspacy
from loguru import logger
from quickumls import QuickUMLS

from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._nlp_result import NLPResult, NLPResultItem
from nre_pipeline.processor import Processor


class MedspacyUmlsProcessor(Processor):
    def __init__(self, processor_id: int) -> None:
        self._quickumls_path = os.getenv("QUICKUMLS_PATH", None)
        if self._quickumls_path is None:
            raise ValueError("QUICKUMLS_PATH must be specified in the configuration.")

        super().__init__(processor_id)

        # Initialize QuickUMLS with the specified path

        self.matcher = QuickUMLS(Path(self._quickumls_path))

        # Create and configure the medspacy pipeline
        self.nlp = medspacy.load()

    def _call(self, document_batch: DocumentBatch) -> Generator[NLPResult, Any, None]:
        for doc in document_batch._documents:
            try:
                # Process text with medspacy
                medspacy_doc = self.nlp(doc.text)

                # Extract UMLS concepts using QuickUMLS
                umls_matches = self.matcher.match(doc.text)

                # Create result items for each concept

                for match_group in umls_matches:
                    for match in match_group:
                        result_items: List[NLPResultItem] = [
                            NLPResultItem("term", match["term"]),
                            NLPResultItem("cui", match["cui"]),
                            NLPResultItem("similarity", match["similarity"]),
                            NLPResultItem("semtypes", match["semtypes"]),
                            NLPResultItem("pos_start", match["start"]),
                            NLPResultItem("pos_end", match["end"]),
                        ]

                        yield NLPResult(note_id=doc.note_id, results=result_items)

            except Exception as e:
                logger.error(f"Error processing document {doc.note_id}: {e}")
                # Yield an empty result in case of error
                yield NLPResult(note_id=doc.note_id, results=[])
