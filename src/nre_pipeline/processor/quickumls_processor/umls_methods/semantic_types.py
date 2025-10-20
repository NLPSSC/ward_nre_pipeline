# Taken from https://documentation.uts.nlm.nih.gov/scripts/get_semantic_types_for_a_list_of_strings.py

from typing import Any, Generator, List, Optional, Tuple
import requests
import argparse
from loguru import logger

from nre_pipeline.processor.quickumls_processor.umls_methods._umls_common_methods import (
    UMLSSemanticType,
    UMLSTerm,
)
from nre_pipeline.processor.quickumls_processor.umls_methods.custom_exceptions import (
    EarlyTerminationError,
)
from nre_pipeline.processor.quickumls_processor.umls_methods.term_search import (
    find_concepts_for_term,
)

# import json
""" The standard Python library argparse is used to incorporate the parsing of command line arguments. 
Instead of manually setting variables in the code, argparse adds flexibility and reusability by allowing user input values to be parsed and utilized."""

BASE_URI = "https://uts-ws.nlm.nih.gov"


# def find_semantic_types_by_single_term(
#     apikey: str,
#     search_string: str,
#     version: str = "current",
#     search_type: Optional[str] = None,
#     vocabularies: Optional[List[str]] = None,
# ) -> Generator[Tuple[List[Any], str], Any, None]:
#     page = 0

#     string_cui_dict = {}

#     while True:
#         page += 1
#         path = "/search/" + version
#         query = {
#             "string": search_string,
#             "apiKey": apikey,
#             "rootSource": vocabularies,
#             "searchType": search_type,
#             "pageNumber": page,
#         }
#         _response = requests.get(BASE_URI + path, params=query)
#         _response.encoding = "utf-8"

#         r = _response.json()

#         try:
#             items = ([r["result"]])[0]["results"]
#         except KeyError as e:
#             logger.error(_response.reason)
#             logger.error(_response.status_code)
#             raise (e)

#         if len(items) == 0:
#             if page == 1:
#                 logger.error("No results found for" + search_string + "\n")
#                 break
#             else:
#                 break

#         yield [rename_keys(item) for item in items], search_string


def get_semantic_type_for_concept(
    apikey: str, cui: str, version: str = "current"
) -> UMLSSemanticType:
    path = "/content/" + version + "/CUI/" + cui
    query = {"apiKey": apikey}
    _response = requests.get(BASE_URI + path, params=query)
    _response.encoding = "utf-8"
    if _response.status_code != 200:
        raise EarlyTerminationError(_response)
    _response_json = _response.json()

    results = _response_json["result"]
    umls_semantic_type = UMLSSemanticType(
        cui=results["ui"],
        term=results["name"],
        semantic_types=[r["name"] for r in results["semanticTypes"]],
    )
    return umls_semantic_type


def find_semantic_types_by_terms(
    apikey: str,
    search_strings: List[str],
    version="current",
    searchtype: Optional[str] = None,
    vocabularies: Optional[List[str]] = None,
) -> Generator[tuple[UMLSSemanticType, str], Any, None]:
    for string in search_strings:
        terms: List[UMLSTerm]
        for terms, _search_string in find_concepts_for_term(apikey, string):
            for uml_item in terms:
                try:
                    umls_semantic_type: UMLSSemanticType = (
                        get_semantic_type_for_concept(apikey, uml_item.cui, version)
                    )
                except EarlyTerminationError as e:
                    logger.error(
                        f"Error occurred while fetching semantic type for {uml_item.cui}: {e}"
                    )
                    raise
                yield umls_semantic_type, _search_string


def run_semantic_types():
    # initialize parser
    parser = argparse.ArgumentParser(description="process user given parameters")

    # add arguments
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
        help="enter version example-2015AA",
    )
    parser.add_argument(
        "-o",
        "--outputfile",
        required=True,
        dest="outputfile",
        help="enter a name for your output file",
    )
    parser.add_argument(
        "-s",
        "--sabs",
        required=False,
        dest="sabs",
        help="enter a comma-separated list of vocabularies, like MSH, SNOMEDCT_US, or RXNORM",
    )
    parser.add_argument(
        "-i",
        "--inputfile",
        required=True,
        dest="inputfile",
        help="enter a name for your input file",
    )
    parser.add_argument(
        "-t",
        "--searchtype",
        required=False,
        dest="searchtype",
        help="enter a searchtype",
    )

    # parse the arguments
    args = parser.parse_args()
    apikey = args.apikey
    version = args.version
    outputfile = args.outputfile
    inputfile = args.inputfile
    sabs = args.sabs
    searchtype = args.searchtype


if __name__ == "__main__":
    import pprint

    items: Generator[Tuple[UMLSSemanticType, str], Any, None] = (
        find_semantic_types_by_terms("c6ab2ac2-ba6e-443a-9b12-1a1a58dec50c", ["pain"])
    )

    try:
        for umls_semantic_type, search_string in items:
            logger.debug("Search String: {}", search_string)
            logger.debug(umls_semantic_type)
    except EarlyTerminationError as e:
        logger.error(f"Error occurred while fetching semantic types: {e}")
