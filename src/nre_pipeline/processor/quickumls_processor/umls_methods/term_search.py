# Taken from https://documentation.uts.nlm.nih.gov/scripts/search-terms.py

import argparse
from typing import Any, Generator, List, Tuple
import requests
from loguru import logger

from nre_pipeline.processor.quickumls_processor.umls_methods._umls_common_methods import (
    UMLSTerm,
)


def find_concepts_for_term(
    apikey: str, search_term: str, version="current"
) -> Generator[Tuple[List[UMLSTerm], str], Any, None]:
    uri = "https://uts-ws.nlm.nih.gov"
    content_endpoint = "/rest/search/" + version
    full_url = uri + content_endpoint
    page = 0

    try:
        while True:
            page += 1
            query = {"string": search_term, "apiKey": apikey, "pageNumber": page}
            # query['includeObsolete'] = 'true'
            # query['includeSuppressible'] = 'true'
            # query['returnIdType'] = "sourceConcept"
            # query['sabs'] = "SNOMEDCT_US"
            r = requests.get(full_url, params=query)
            r.raise_for_status()
            r.encoding = "utf-8"
            outputs = r.json()

            items = (([outputs["result"]])[0])["results"]

            if len(items) == 0:
                if page == 1:
                    print("No results found." + "\n")
                    break
                else:
                    break

            yield [
                UMLSTerm(item["ui"], item["name"], item["rootSource"]) for item in items
            ], search_term

    except Exception as except_error:
        logger.error(except_error)


def results_list():
    parser = argparse.ArgumentParser(description="process user given parameters")
    parser.add_argument(
        "-k",
        "--apikey",
        required=True,
        dest="apikey",
        help="enter api key from your UTS Profile",
    )
    parser.add_argument(
        "-v",
        "--version",
        required=False,
        dest="version",
        default="current",
        help="enter version example-2021AA",
    )
    parser.add_argument(
        "-s",
        "--string",
        required=True,
        dest="string",
        help="enter a search term, using hyphens between words, like diabetic-foot",
    )

    args = parser.parse_args()
    apikey = args.apikey
    version = args.version
    string = args.string

    return find_concepts_for_term(apikey, version, string)


if __name__ == "__main__":
    import pprint

    for items, search_term in find_concepts_for_term(
        "c6ab2ac2-ba6e-443a-9b12-1a1a58dec50c", "diabetic-foot"
    ):

        logger.debug(f"Search Term: {search_term}")
        logger.debug(pprint.pformat(items, indent=4, width=80))
        logger.debug("")
