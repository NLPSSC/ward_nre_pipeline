import json
from pathlib import Path
from loguru import logger
from typing import Dict
from ..from_csv.to_dict_lookup_methods import (
    make_nested_lookup_path,
)
from ..models.consts import HeaderLabel
from ..models.quickumls_counters import (
    QuickUMLSCounters,
    QuickUmlsCounter,
)


def calculate_metrics(
    counter: QuickUMLSCounters| Path,
):

    if isinstance(counter, Path):
        # Load the counter from a file if a Path is provided
        with open(counter, "r", encoding="utf-8") as f:
            counter = QuickUMLSCounters.from_dict(json.load(f))

    # notes
    note_counter: QuickUmlsCounter = counter.note_id_counter
    num_notes = note_counter.count("total_entries")

    # cuis
    cui_counter: QuickUmlsCounter = counter.cui_counter
    num_cuis = cui_counter.count("unique_entries")

    # terms
    term_counter: QuickUmlsCounter = counter.term_counter
    num_terms = term_counter.count("unique_entries")

    # ngrames
    ngram_counter: QuickUmlsCounter = counter.ngram_counter
    num_ngrams = ngram_counter.count("unique_entries")

    # semantic types
    semantic_type_counter: QuickUmlsCounter = counter.semantic_type_counter
    num_semantic_types = semantic_type_counter.count("unique_entries")

    # similarities
    similarity_counter: QuickUmlsCounter = counter.similarity_counter
    num_similarities = similarity_counter.count("unique_entries")

    lookup_file = make_nested_lookup_path(lookup_output_path)

    if not lookup_file.exists():
        logger.error(f"Lookup file not found: {lookup_file}")
        return

    with open(lookup_file, "r", encoding="utf-8") as f:
        nested_lookup = json.load(f)

    logger.info(f"Loaded nested lookup from: {lookup_file}")
