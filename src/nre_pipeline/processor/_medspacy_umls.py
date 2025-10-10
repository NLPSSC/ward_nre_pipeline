import os
from pathlib import Path
from typing import Any, Generator, List

from loguru import logger

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
        from quickumls import QuickUMLS

        self._matcher = QuickUMLS(Path(self._quickumls_path))

        # Create and configure the medspacy pipeline
        import medspacy

        self._nlp = medspacy.load()

        from spacy_symspell import SpellingCorrector

        corrector = SpellingCorrector()

        # Add a component to remove stop words
        def remove_stopwords(doc):
            doc_without_stop = [token for token in doc if not token.is_stop]
            doc._.filtered_text = " ".join([token.text for token in doc_without_stop])
            return doc

        from spacy.tokens import Doc as SpacyDoc

        if not SpacyDoc.has_extension("filtered_text"):
            SpacyDoc.set_extension("filtered_text", default=None)
        if not self._nlp.has_pipe("remove_stopwords"):
            from spacy.language import Language

            Language.component("remove_stopwords", func=remove_stopwords)
            self._nlp.add_pipe("remove_stopwords", last=True)

        # Add a component to correct spelling
        def correct_spelling(doc):
            corrected = corrector(doc)
            doc._.corrected_text = corrected.text
            return doc

        self._nlp.add_pipe(corrector, last=True)

    def _call(self, document_batch: DocumentBatch) -> Generator[NLPResult, Any, None]:
        for doc in document_batch._documents:
            try:
                # Process text with medspacy
                self._nlp(doc.text)

                # Extract UMLS concepts using QuickUMLS
                umls_matches = self._matcher.match(doc.text)

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
