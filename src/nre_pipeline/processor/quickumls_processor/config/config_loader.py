import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from loguru import logger


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
    return load_config(Path(__file__).parent / f"default_{metric}.yml")


def load_config(config_path: Path) -> Dict[str, Any]:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def get_quickumls_config(quickumls_config) -> Dict[str, Any] | None:
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

    quickumls_config_path = quickumls_config.get("quickumls_config_path", None)
    metric = quickumls_config.get("metric", None)
    config: Dict[str, Any] | None = None
    if quickumls_config_path is not None:
        config = load_config(quickumls_config_path)
    elif metric is not None:
        config = load_default_config(metric)
    else:
        logger.error("No valid QuickUMLS configuration path or metric provided.")
        raise ValueError("No valid QuickUMLS configuration path or metric provided.")

    # if quick_umls_parameters is not None:
    #     if quick_umls_parameters.threshold is not None:
    #         config["threshold"] = float(quick_umls_parameters.threshold)
    #     if quick_umls_parameters.similarity_name is not None:
    #         config["similarity_name"] = quick_umls_parameters.similarity_name
    #     if quick_umls_parameters.window is not None:
    #         config["window"] = int(quick_umls_parameters.window)
    #     if quick_umls_parameters.min_match_length is not None:
    #         config["min_match_length"] = int(quick_umls_parameters.min_match_length)
    #     if quick_umls_parameters.ignore_syntax is not None:
    #         config["ignore_syntax"] = bool(quick_umls_parameters.ignore_syntax)
    #     if quick_umls_parameters.best_match is not None:
    #         config["best_match"] = bool(quick_umls_parameters.best_match)
    #     if quick_umls_parameters.verbose is not None:
    #         config["verbose"] = bool(quick_umls_parameters.verbose)
    #     if quick_umls_parameters.accepted_semtypes is not None:
    #         config["accepted_semtypes"] = set(quick_umls_parameters.accepted_semtypes)

    return config
