import os
import sys
import threading
from pathlib import Path
from typing import Any, Dict, Generator, List, Literal, Optional

from loguru import logger
import requests

from nre_pipeline.models._nlp_result import NLPResultFeatures
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._nlp_result_item import NLPResultFeature
from nre_pipeline.processor import Processor
from quickumls import QuickUMLS

TGT_URL = f"https://utslogin.nlm.nih.gov/cas/v1/api-key"
BASE_URL = "https://uts-ws.nlm.nih.gov/rest"


class UMLSRestApiClient:

    def __init__(self) -> None:
        api_key = os.getenv("UMLS_API_KEY")
        if not api_key:
            dev_umls_key_path = os.getenv("DEV_UMLS_KEY_PATH")
            if not dev_umls_key_path:
                raise ValueError(
                    "Either UMLS_API_KEY must be defined or the DEV_UMLS_KEY_PATH must be defined."
                )
            api_key = Path(dev_umls_key_path).read_text().strip()
        self._api_key: str = api_key

    def get_umls_concepts(self, text: str) -> List[Dict[str, Any]]:
        """
        Calls the UMLS REST API to get UMLS concepts for the given search string.
        Returns a list of concept dicts.
        """

        # Get a ticket granting ticket (TGT)
        tgt_resp = requests.post(TGT_URL, data={"apikey": self._api_key})
        if tgt_resp.status_code != 201:
            raise Exception("Failed to get UMLS TGT")
        tgt = tgt_resp.headers["location"]

        # Get a service ticket (ST)
        st_resp = requests.post(tgt, data={"service": BASE_URL})
        if st_resp.status_code != 200:
            raise Exception("Failed to get UMLS service ticket")
        service_ticket = st_resp.text

        # Search for concepts
        search_url = f"{BASE_URL}/search/current"
        params = {
            "string": text,
            "ticket": service_ticket,
            "pageSize": 10,
        }
        resp = requests.get(search_url, params=params)
        resp.raise_for_status()
        results = resp.json()["result"]["results"]
        return results

    def get_semantic_types_by_concept(self, concept: Dict[str, Any]) -> List[str]:
        # Implement REST API call to UMLS
        pass


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

    # Class-level shared matcher to avoid redundant initialization
    _shared_matcher: Optional[QuickUMLS] = None
    _matcher_lock = threading.Lock()

    def __init__(
        self, metric: Literal["cosine", "jaccard", "levenshtein"], *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._matcher: QuickUMLS = self._get_shared_matcher()
        self._metric = metric
        # get_quickumls_config

    @classmethod
    def _get_shared_matcher(cls) -> QuickUMLS:
        """Get or create a shared QuickUMLS matcher instance."""
        if cls._shared_matcher is None:
            with cls._matcher_lock:
                if cls._shared_matcher is None:  # Double-check locking
                    try:
                        quickumls_path: Path = cls._init_quickumls_path()
                        logger.info(
                            f"Initializing shared QuickUMLS matcher at {quickumls_path}"
                        )
                        try:

                            # Prefer Levenshtein distance if supported by the QuickUMLS constructor.
                            cls._shared_matcher = QuickUMLS(
                                quickumls_path, similarity_name="levenshtein"
                            )
                        except TypeError:
                            # Older/newer QuickUMLS versions may not accept similarity_name; fall back gracefully.
                            logger.warning(
                                "QuickUMLS constructor does not accept 'similarity_name'; using default similarity metric."
                            )
                            cls._shared_matcher = QuickUMLS(quickumls_path)
                        logger.info(
                            "Shared QuickUMLS matcher initialized successfully."
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to initialize QuickUMLS matcher: {e}",
                            exc_info=True,
                        )
                        raise
        return cls._shared_matcher

    def _call_processor(
        self, document_batch: DocumentBatch
    ) -> Generator[NLPResultFeatures, Any, None]:
        total_found_in_batch = 0
        for doc in document_batch._documents:
            try:
                # Extract UMLS concepts using QuickUMLS
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
                        yield NLPResultFeatures(
                            note_id=doc.note_id, result_features=result_items
                        )
            except Exception as e:
                logger.error(
                    f"Error processing document {doc.note_id}: {e}", exc_info=True
                )
                yield NLPResultFeatures(note_id=doc.note_id, result_features=[])

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

if __name__ == "__main__":
    umls_rest_api_client = UMLSRestApiClient()
    concepts = umls_rest_api_client.get_umls_concepts("cirrhosis")