import os
from pathlib import Path
from typing import Any, Generator, List

from loguru import logger

from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._nlp_result import NLPResult, NLPResultItem
from nre_pipeline.processor import Processor
from quickumls import QuickUMLS


class MedspacyUmlsProcessor(Processor):
    def __init__(self, processor_id: int) -> None:
        self._quickumls_path = os.getenv("QUICKUMLS_PATH", None)
        if self._quickumls_path is None:
            raise ValueError("QUICKUMLS_PATH must be specified in the configuration.")

        super().__init__(processor_id)

        # Log the QuickUMLS path for debugging
        logger.info(f"QuickUMLS path: {self._quickumls_path}")

        # Verify the path exists
        quickumls_path_obj = Path(self._quickumls_path)
        if not quickumls_path_obj.exists():
            raise ValueError(f"QuickUMLS path does not exist: {self._quickumls_path}")

        # Check for required QuickUMLS files
        required_files = [
            "database_backend.flag",
            "language.flag",
            "cui-semtypes.db",
            "umls-simstring.db",
        ]
        for required_file in required_files:
            file_path = quickumls_path_obj / required_file
            if not file_path.exists():
                logger.warning(f"Required QuickUMLS file missing: {file_path}")
            else:
                logger.info(f"Found QuickUMLS file: {file_path}")

        # Initialize QuickUMLS with the specified path
        try:
            self._matcher = QuickUMLS(quickumls_path_obj)
            logger.info("QuickUMLS matcher initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize QuickUMLS: {e}")
            raise

        # # Create and configure the medspacy pipeline
        # self._nlp = spacy.load("en_core_web_sm")

        # # Add the medspacy_quickumls component (already registered in spaCy)
        # self._nlp.add_pipe(
        #     "medspacy_quickumls", config={"quickumls_path": str(self._quickumls_path)}
        # )

        logger.info("MedspacyUmlsProcessor initialized.")

        # # Add a component to remove stop words
        # def remove_stopwords(doc):
        #     doc_without_stop = [token for token in doc if not token.is_stop]
        #     doc._.filtered_text = " ".join([token.text for token in doc_without_stop])
        #     return doc

        # if not SpacyDoc.has_extension("filtered_text"):
        #     SpacyDoc.set_extension("filtered_text", default=None)
        # if not self._nlp.has_pipe("remove_stopwords"):
        #     Language.component("remove_stopwords", func=remove_stopwords)
        #     self._nlp.add_pipe("remove_stopwords", last=True)

    def _call(self, document_batch: DocumentBatch) -> Generator[NLPResult, Any, None]:
        for doc in document_batch._documents:
            try:
                # Log document info for debugging
                logger.debug(
                    f"Processing document {doc.note_id}, text length: {len(doc.text)}"
                )
                logger.debug(f"Document text preview: {doc.text[:200]}...")

                # Extract UMLS concepts using QuickUMLS
                umls_matches = self._matcher.match(doc.text)

                # Log matching results
                logger.debug(
                    f"QuickUMLS returned {len(umls_matches)} match groups for document {doc.note_id}"
                )

                if not umls_matches:
                    logger.debug(f"No UMLS matches found for document {doc.note_id}")
                    # Try a simple test with known medical terms
                    test_text = "diabetes mellitus hypertension"
                    test_matches = self._matcher.match(test_text)
                    logger.debug(
                        f"Test match on '{test_text}': {len(test_matches)} groups found"
                    )

                match_count = 0
                # Create result items for each concept
                for match_group in umls_matches:
                    logger.debug(
                        f"Processing match group with {len(match_group)} matches"
                    )
                    for match in match_group:
                        match_count += 1
                        logger.debug(f"Match {match_count}: {match}")

                        result_items: List[NLPResultItem] = [
                            NLPResultItem("term", match["term"]),
                            NLPResultItem("cui", match["cui"]),
                            NLPResultItem("similarity", match["similarity"]),
                            NLPResultItem("semtypes", match["semtypes"]),
                            NLPResultItem("pos_start", match["start"]),
                            NLPResultItem("pos_end", match["end"]),
                        ]
                        yield NLPResult(note_id=doc.note_id, results=result_items)

                logger.info(
                    f"Found {match_count} UMLS matches for document {doc.note_id}"
                )

            except Exception as e:
                logger.error(f"Error processing document {doc.note_id}: {e}")
                # Yield an empty result in case of error
                yield NLPResult(note_id=doc.note_id, results=[])
