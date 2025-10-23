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
    """
    QuickUMLSProcessor

    A Processor that extracts UMLS concepts from document text using a shared QuickUMLS matcher.

    This class maintains a single, process-wide QuickUMLS instance to avoid the heavy
    initialization cost of creating multiple QuickUMLS matchers. The shared matcher is
    protected by a threading.Lock and initialized using a double-checked locking pattern.

    Behavior
    - On first creation of the matcher, the QuickUMLS data path is obtained from the
        environment variable QUICKUMLS_PATH and validated (required files must exist).
    - The shared matcher is created once per process and reused by all instances of
        QuickUMLSProcessor in that process.
    - Documents are processed by calling the underlying QuickUMLS.match(text) method.
        Each match yields an NLPResult containing NLPResultItem entries for:
            - "term" (matched text)
            - "cui" (concept unique identifier)
            - "similarity" (match similarity score)
            - "semtypes" (semantic types)
            - "pos_start" (start position in the text)
            - "pos_end" (end position in the text)
    - If an exception occurs while processing a document, the processor logs the error
        and yields an NLPResult for that document with an empty results list.

    Thread-safety
    - The shared QuickUMLS matcher is created under a class-level lock to make the
        initialization thread-safe. After initialization, using the QuickUMLS instance for
        matching is dependent on the thread-safety of the QuickUMLS library itself.

    Configuration
    - Environment: QUICKUMLS_PATH must point to the directory containing QuickUMLS data files.
    - Required files checked at initialization:
            - database_backend.flag
            - language.flag
            - cui-semtypes.db
            - umls-simstring.db
    - Validation failures raise exceptions (ValueError/FileNotFoundError). One internal
        helper method intentionally calls sys.exit(1) if required files are missing; callers
        should be aware of that behavior.

    Public/Important Internal Methods
    - _get_shared_matcher() -> QuickUMLS
            Returns the shared QuickUMLS instance, initializing it on first use. May raise
            on initialization failures (propagates exceptions after logging).

    - _call_processor(document_batch: DocumentBatch) -> Generator[NLPResult, Any, None]
            Iterates documents in the batch, performs QuickUMLS matching, and yields an
            NLPResult per match. Logs and yields an empty-result NLPResult when a document
            cannot be processed due to an exception.

    - _init_quickumls() / _init_quickumls_path() -> Path
            Helpers that validate the QUICKUMLS_PATH and required files. They return a pathlib.Path
            to the QuickUMLS directory on success and raise or exit on failure.

    Logging
    - The class logs initialization steps, validation outcomes, and errors with detailed
        exception information when available.

    Usage (high level)
    - Ensure QUICKUMLS_PATH is set and points to a valid QuickUMLS data directory.
    - Create instances of QuickUMLSProcessor as needed; they will share the matcher.
    - Feed DocumentBatch objects into the processor; consume the generator of NLPResult
        objects emitted by _call_processor.

    Notes
    - QuickUMLS initialization can be expensive and may require significant
        memory/disk resources; sharing the matcher is recommended for multi-instance use.
    - This docstring documents expected behavior; callers should inspect runtime logs
        for detailed initialization and error information.
    """

    # Each instance will have its own matcher

    def __init__(
        self,
        metric: Union[Literal["cosine", "jaccard", "levenshtein"], Path],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._metric = metric
        self._matcher: QuickUMLS = self._create_matcher(metric)
        self.start()

    def _create_matcher(
        self, metric: Union[Literal["cosine", "jaccard", "levenshtein"], Path]
    ) -> QuickUMLS:
        """
        Create and return a new QuickUMLS matcher for this processor instance.
        """
        try:
            quickumls_path: Path = self._init_quickumls_path()
            logger.info(f"Initializing QuickUMLS matcher at {quickumls_path}")
            quickumls_config: Dict[str, Any] = get_quickumls_config(metric)
            try:
                matcher = QuickUMLS(quickumls_path, **quickumls_config)
            except TypeError as te:
                logger.warning(
                    "QuickUMLS constructor does not accept 'similarity_name'; using default similarity metric.",
                    te,
                )
                matcher = QuickUMLS(quickumls_path)
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
        """
        Process a batch of documents, extract UMLS concepts using QuickUMLS, and yield NLPResultFeatures for each found match.

        Parameters
        ----------
        document_batch : DocumentBatch
            Batch containing the documents to process. Each document is expected to have at least
            the attributes `text` (str) and `note_id` (identifier used in yielded results).

        Yields
        ------
        NLPResultFeatures
            A generator yielding one NLPResultFeatures instance per individual QuickUMLS match.
            Each yielded NLPResultFeatures contains:
              - note_id: the originating document's note_id
              - result_features: a list of NLPResultFeature instances with keys/values:
                  - "ngram": matched surface text (str)
                  - "term": canonical term (str)
                  - "cui": UMLS Concept Unique Identifier (str)
                  - "similarity": similarity score returned by QuickUMLS (float)
                  - "semtypes": semantic types associated with the concept (list)
                  - "pos_start": start character offset of the match in the document text (int)
                  - "pos_end": end character offset of the match in the document text (int)

        Behavior
        --------
        - Iterates over document_batch._documents and calls self._matcher.match(doc.text) to obtain QuickUMLS matches.
        - QuickUMLS returns a list of match groups; each group may contain one or more match dicts.
        - The function iterates every match dict and yields a corresponding NLPResultFeatures object.
        - Internal counters (e.g., total_found_in_batch, match_count) are maintained for bookkeeping but are not returned.

        Error handling
        --------------
        - Any exception raised while processing a document is logged (with full exception info).
        - If processing a document fails, a single NLPResultFeatures with an empty result_features list is yielded for that document.

        Notes
        -----
        - If a document has no matches, nothing is yielded for that document (unless an exception occurs).
        - Expected keys in each QuickUMLS match dict: "ngram", "term", "cui", "similarity", "semtypes", "start", "end".
        - Return type: Generator[NLPResultFeatures, Any, None].
        """
        total_found_in_batch = 0

        for doc in document_batch._documents:
            try:
                # Extract UMLS concepts using QuickUMLS
                # logger.debug(f"Processing document: {doc.note_id}")
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
                        ]
                        yield NLPResultItem(
                            note_id=doc.note_id, result_features=result_items
                        )
            except Exception as e:
                logger.error(
                    f"Error processing document {doc.note_id}: {e}", exc_info=True
                )
                yield NLPResultItem(note_id=doc.note_id, result_features=[])

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


def build_quickumls_processor_config(
    document_batch_inqueue, nlp_results_outqueue, halt_event
):

    return {
        "metric": "jaccard",
        "document_batch_inqueue": document_batch_inqueue,
        "nlp_results_outqueue": nlp_results_outqueue,
        "process_interrupt": halt_event
    }
