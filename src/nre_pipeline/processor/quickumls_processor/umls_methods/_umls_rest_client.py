# This script will return CUI information for a single search term.
# Optional query parameters are commented out below.


import os
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple
from loguru import logger

from nre_pipeline.processor.quickumls_processor.umls_methods._umls_common_methods import (
    UMLSTerm,
)
from nre_pipeline.processor.quickumls_processor.umls_methods.term_search import (
    find_concepts_for_term,
)


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

    def search_for_terms_by_phrase(
        self, search_text: str
    ) -> Generator[Tuple[List[UMLSTerm], str], Any, None]:
        """
        Calls the UMLS REST API to get UMLS concepts for the given search string.
        Returns a list of concept dicts.
        """

        return find_concepts_for_term(self._api_key, search_text)

    def get_semantic_types_by_concept(self, concept: Dict[str, Any]) -> List[str]:
        # Implement REST API call to UMLS
        return []


if __name__ == "__main__":
    umls_rest_api_client = UMLSRestApiClient()
    umls_terms: Generator[Tuple[List[UMLSTerm], str], Any, None] = (
        umls_rest_api_client.search_for_terms_by_phrase("cirrhosis")
    )

    for terms, search_string in umls_terms:
        logger.debug(f"Search String: {search_string}")
        for term in terms:
            logger.debug(term)
