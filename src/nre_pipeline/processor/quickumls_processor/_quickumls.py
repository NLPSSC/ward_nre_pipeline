import os
import sys
from pathlib import Path
from typing import Any, Dict, Generator, List, Literal, Optional, Set, Union

from loguru import logger

from nre_pipeline.common.base._base_processor import Processor
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._nlp_result_item import NLPResultFeature

from quickumls import QuickUMLS

from nre_pipeline.processor.quickumls_processor.config.config_loader import (
    get_quickumls_config,
)

TGT_URL = f"https://utslogin.nlm.nih.gov/cas/v1/api-key"
BASE_URL = "https://uts-ws.nlm.nih.gov/rest"


def _semantic_types_in_config_to_set(
    semantic_types: Optional[List[str]] = None,
) -> Optional[Set[str]]:
    if not semantic_types:
        return None
    return set(semantic_types)


class QuickUMLSProcessor(Processor):

    def __init__(
        self,
        *args,
        **config,
    ) -> None:
        super().__init__(*args, **config)
        self._matcher: QuickUMLS = self._create_matcher()

    def _create_matcher(self) -> QuickUMLS:
        """
        Create and return a new QuickUMLS matcher for this processor instance.
        """
        try:
            quickumls_path: Path = self._init_quickumls_path()
            logger.info(f"Initializing QuickUMLS matcher at {quickumls_path}")

            quickumls_config: Dict[str, Any] | None = get_quickumls_config(
                self.processor_config
            )
            if quickumls_config is None:
                raise ValueError("QuickUMLS configuration could not be loaded.")

            try:
                matcher = QuickUMLS(quickumls_path, **quickumls_config)
            except TypeError as te:
                logger.warning(
                    "QuickUMLS constructor does not accept 'similarity_name'; using default similarity metric.",
                    te,
                )
                matcher: QuickUMLS = QuickUMLS(quickumls_path)
            logger.info("QuickUMLS matcher initialized successfully.")
        except Exception as e:
            logger.error(
                f"Failed to initialize QuickUMLS matcher: {e}",
                exc_info=True,
            )
            raise
        return matcher

    def _call_processor(
        self, document_batch: DocumentBatch
    ) -> Generator[NLPResultItem, Any, None]:

        total_found_in_batch = 0

        for doc in document_batch._documents:
            try:
                # Extract UMLS concepts using QuickUMLS
                # logger.debug(f"Processing document: {doc.note_id}")
                doc_length = len(doc.text)
                umls_matches = self._matcher.match(doc.text)

                if len(umls_matches) > 0:
                    total_found_in_batch += len(umls_matches)

                match_count = 0
                for match_group in umls_matches:
                    for match in match_group:
                        match_count += 1
                        result_items: List[NLPResultFeature] = [
                            NLPResultFeature("ngram", match["ngram"]),
                            NLPResultFeature("term", match["term"]),
                            NLPResultFeature("cui", match["cui"]),
                            NLPResultFeature("similarity", match["similarity"]),
                            NLPResultFeature("semtypes", match["semtypes"]),
                            NLPResultFeature("pos_start", match["start"]),
                            NLPResultFeature("pos_end", match["end"]),
                            NLPResultFeature("doc_length", doc_length),
                        ]
                        yield NLPResultItem(
                            note_id=doc.note_id, result_features=result_items
                        )
            except Exception as e:
                logger.error(
                    f"Error processing document {doc.note_id}: {e}", exc_info=True
                )
                yield NLPResultItem(note_id=doc.note_id, result_features=[])

    @classmethod
    def _init_quickumls_path(cls) -> Path:
        """Initialize and validate QuickUMLS path."""
        quickumls_path = os.getenv("QUICKUMLS_PATH", None)
        if quickumls_path is None:
            raise ValueError("QUICKUMLS_PATH must be specified in the configuration.")
        if os.path.exists(quickumls_path) is False:
            raise ValueError(f"QuickUMLS path does not exist: {quickumls_path}")

        logger.debug(f"QuickUMLS path: {quickumls_path}")

        quickumls_path_obj = Path(quickumls_path)

        required_files = [
            "database_backend.flag",
            "language.flag",
            "cui-semtypes.db",
            "umls-simstring.db",
        ]
        for required_file in required_files:
            file_path = quickumls_path_obj / required_file
            if not file_path.exists():
                logger.error(f"Required QuickUMLS file missing: {file_path}")
                raise FileNotFoundError(f"Required QuickUMLS file missing: {file_path}")

        logger.info("QuickUMLS path validated.")
        return quickumls_path_obj


##################################################################################
# I don't believe this is needed anymore
##################################################################################
# def build_quickumls_processor_config(
#     document_batch_inqueue, nlp_results_outqueue, halt_event
# ):

#     return {
#         "metric": "jaccard",
#         "document_batch_inqueue": document_batch_inqueue,
#         "nlp_results_outqueue": nlp_results_outqueue,
#         "process_interrupt": halt_event,
#     }


##################################################################################
# I think this is a duplicate
##################################################################################
# def _init_quickumls(self):
#     quickumls_path = os.getenv("QUICKUMLS_PATH", None)
#     if quickumls_path is None:
#         raise ValueError("QUICKUMLS_PATH must be specified in the configuration.")

#     # Log the QuickUMLS path for debugging
#     logger.debug(f"QuickUMLS path: {quickumls_path}")

#     # Verify the path exists
#     quickumls_path_obj = Path(quickumls_path)
#     if not quickumls_path_obj.exists():
#         raise ValueError(f"QuickUMLS path does not exist: {quickumls_path}")

#     # Check for required QuickUMLS files
#     required_files = [
#         "database_backend.flag",
#         "language.flag",
#         "cui-semtypes.db",
#         "umls-simstring.db",
#     ]
#     for required_file in required_files:
#         file_path = quickumls_path_obj / required_file
#         if not file_path.exists():
#             logger.error(
#                 f"Required QuickUMLS file missing: {file_path}; exiting tool"
#             )
#             sys.exit(1)

#     return quickumls_path_obj
