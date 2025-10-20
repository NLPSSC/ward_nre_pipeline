from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
import yaml


@dataclass
class QuickUMLSConfig:
    """Dataclass representing QuickUMLS matcher configuration."""

    metric: Literal["cosine", "jaccard", "levenshtein"]
    quickumls_fp: Optional[str] = None
    threshold: Optional[float] = None
    similarity_name: Optional[str] = None
    window: Optional[int] = None
    min_match_length: Optional[int] = None
    ignore_syntax: Optional[bool] = None
    best_match: Optional[bool] = None
    verbose: Optional[bool] = None
    accepted_semtypes: Optional[List[str]] = None


def load_default_config(
    metric: Literal["cosine", "jaccard", "levenshtein"],
) -> Dict[str, Any]:
    with open(f"./default_{metric}.yml", "r") as f:
        config = yaml.safe_load(f)
    return config


def get_quickumls_config(
    metric: Literal["cosine", "jaccard", "levenshtein"],
    quick_umls_parameters: Optional[QuickUMLSConfig] = None,
) -> Dict[str, Any]:
    """Get the configuration for the QuickUMLS matcher.

    Returns:
        Dict[str, Any]: A dictionary containing configuration settings.

    Example return value...

    config = {
        "quickumls_fp": "/path/to/quickumls_data",  # Path to QuickUMLS data directory
        "threshold": 0.8,                           # Jaccard similarity threshold
        "similarity_name": "jaccard",               # Use Jaccard similarity
        "window": 5,                                # Number of tokens in matching window
        "min_match_length": 3,                      # Minimum length of match
        "ignore_syntax": False,                     # Whether to ignore syntax filtering
        "best_match": True,                         # Return only best match per span
        "verbose": False,                           # Verbose logging
        "accepted_semtypes": None                   # Restrict to certain semantic types (None for all)
    }

    """

    # threshold: Optional[float] = None,
    # similarity_name: Optional[str] = None,
    # window: Optional[int] = None,
    # min_match_length: Optional[int] = None,
    # ignore_syntax: Optional[bool] = None,
    # best_match: Optional[bool] = None,
    # verbose: Optional[bool] = None,
    # accepted_semtypes: Optional[List[str]] = None,

    config: Dict[str, Any] = load_default_config(metric)
    if quick_umls_parameters is not None:
        if quick_umls_parameters.threshold is not None:
            config["threshold"] = quick_umls_parameters.threshold
        if quick_umls_parameters.similarity_name is not None:
            config["similarity_name"] = quick_umls_parameters.similarity_name
        if quick_umls_parameters.window is not None:
            config["window"] = quick_umls_parameters.window
        if quick_umls_parameters.min_match_length is not None:
            config["min_match_length"] = quick_umls_parameters.min_match_length
        if quick_umls_parameters.ignore_syntax is not None:
            config["ignore_syntax"] = quick_umls_parameters.ignore_syntax
        if quick_umls_parameters.best_match is not None:
            config["best_match"] = quick_umls_parameters.best_match
        if quick_umls_parameters.verbose is not None:
            config["verbose"] = quick_umls_parameters.verbose
        if quick_umls_parameters.accepted_semtypes is not None:
            config["accepted_semtypes"] = quick_umls_parameters.accepted_semtypes

    return config
