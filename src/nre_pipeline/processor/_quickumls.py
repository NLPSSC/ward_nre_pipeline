import os
import sys
import threading
from pathlib import Path
from typing import Any, Generator, List, Optional

from loguru import logger

from nre_pipeline.models._nlp_result import NLPResult
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._nlp_result_item import NLPResultItem
from nre_pipeline.processor import Processor
from quickumls import QuickUMLS


class QuickUMLSProcessor(Processor):
    # Class-level shared matcher to avoid redundant initialization
    _shared_matcher: Optional[QuickUMLS] = None
    _matcher_lock = threading.Lock()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._matcher = self._get_shared_matcher()

    @classmethod
    def _get_shared_matcher(cls) -> QuickUMLS:
        """Get or create a shared QuickUMLS matcher instance."""
        if cls._shared_matcher is None:
            with cls._matcher_lock:
                if cls._shared_matcher is None:  # Double-check locking
                    quickumls_path = cls._init_quickumls_path()
                    logger.info(
                        f"Initializing shared QuickUMLS matcher at {quickumls_path}"
                    )
                    cls._shared_matcher = QuickUMLS(quickumls_path)
                    logger.info("Shared QuickUMLS matcher initialized successfully.")
        return cls._shared_matcher

    def _call_processor(
        self, document_batch: DocumentBatch
    ) -> Generator[NLPResult, Any, None]:
        total_found_in_batch = 0
        for doc in document_batch._documents:
            try:
                # Log document info for debugging
                # logger.debug(
                #     f"Processing document {doc.note_id}, text length: {len(doc.text)}"
                # )

                # Extract UMLS concepts using QuickUMLS
                umls_matches = self._matcher.match(doc.text)

                # Log matching results, if found
                if len(umls_matches) > 0:
                    total_found_in_batch += len(umls_matches)

                match_count = 0
                # Create result items for each concept
                for match_group in umls_matches:
                    # logger.debug(
                    #     f"Processing match group with {len(match_group)} matches"
                    # )
                    for match in match_group:
                        match_count += 1
                        # logger.debug(f"Match {match_count}: {match}")

                        result_items: List[NLPResultItem] = [
                            NLPResultItem("term", match["term"]),
                            NLPResultItem("cui", match["cui"]),
                            NLPResultItem("similarity", match["similarity"]),
                            NLPResultItem("semtypes", match["semtypes"]),
                            NLPResultItem("pos_start", match["start"]),
                            NLPResultItem("pos_end", match["end"]),
                        ]
                        yield NLPResult(note_id=doc.note_id, results=result_items)

                # logger.info(
                #     f"Found {match_count} UMLS matches for document {doc.note_id}"
                # )

            except Exception as e:
                logger.error(f"Error processing document {doc.note_id}: {e}")
                # Yield an empty result in case of error
                yield NLPResult(note_id=doc.note_id, results=[])

    def _init_quickumls(self):
        quickumls_path = os.getenv("QUICKUMLS_PATH", None)
        if quickumls_path is None:
            raise ValueError("QUICKUMLS_PATH must be specified in the configuration.")

        # Log the QuickUMLS path for debugging
        logger.debug(f"QuickUMLS path: {quickumls_path}")

        # Verify the path exists
        quickumls_path_obj = Path(quickumls_path)
        if not quickumls_path_obj.exists():
            raise ValueError(f"QuickUMLS path does not exist: {quickumls_path}")

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
                logger.error(
                    f"Required QuickUMLS file missing: {file_path}; exiting tool"
                )
                sys.exit(1)

        return quickumls_path_obj

    @classmethod
    def _init_quickumls_path(cls) -> Path:
        """Initialize and validate QuickUMLS path."""
        quickumls_path = os.getenv("QUICKUMLS_PATH", None)
        if quickumls_path is None:
            raise ValueError("QUICKUMLS_PATH must be specified in the configuration.")

        # Log the QuickUMLS path for debugging
        logger.debug(f"QuickUMLS path: {quickumls_path}")

        # Verify the path exists
        quickumls_path_obj = Path(quickumls_path)
        if not quickumls_path_obj.exists():
            raise ValueError(f"QuickUMLS path does not exist: {quickumls_path}")

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
                logger.error(
                    f"Required QuickUMLS file missing: {file_path}; exiting tool"
                )
                sys.exit(1)

        logger.info("QuickUMLS path validated.")
        return quickumls_path_obj
