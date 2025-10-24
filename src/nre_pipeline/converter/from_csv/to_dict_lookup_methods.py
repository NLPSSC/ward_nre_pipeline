import io
import json
import csv
from pathlib import Path
from typing import Any, Counter, Dict, List, Literal, Tuple, TypeAlias, Union, cast
from loguru import logger

ASCII_COLORS: List[str] = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
    "\033[97m",  # White
]

RESET_COLOR = "\033[0m"

HeaderLabel: TypeAlias = Literal[
    "note_id",
    "ngram",
    "term",
    "cui",
    "similarity",
    "semtypes",
    "pos_start",
    "pos_end",
    "doc_length",
]


def load_quickumls_results(src, ngram_to_lower_case: bool):
    data_rows = load_reader(src, delimeter="|")  # 1) Load the file into a CSV reader
    sample_row, header, data_row_iter = get_sample_header_and_data_iter(
        data_rows, ngram_to_lower_case
    )  # Find the first row where each field has at least three characters
    return (
        sample_row,
        cast(List[HeaderLabel], [cast(HeaderLabel, h) for h in header]),
        data_row_iter,
    )


def build_nested_lookup(
    header: List[HeaderLabel],
    rows,
    selected_headers,
    unused_headers,
    header_index_map: Dict[HeaderLabel, int],
) -> Tuple[Dict[Any, Any], Dict[str, Counter[Any]]]:
    """Use the selected headers to efficiently create a nested dictionary lookup structure.

    Args:
        header (_type_): _description_
        rows (_type_): _description_
        selected_headers (_type_): _description_
        unused_headers (_type_): _description_

    Returns:
        _type_: _description_
    """
    lookup = {}

    cui_index: int = header_index_map["cui"]
    term_index: int = header_index_map["term"]
    similarity_index: int = header_index_map["similarity"]
    ngram_index: int = header_index_map["ngram"]
    pos_start_index: int = header_index_map["pos_start"]
    pos_end_index: int = header_index_map["pos_end"]
    doc_length_index: int = header_index_map["doc_length"]
    semantic_type_index: int = header_index_map["semtypes"]
    note_id_index: int = header_index_map["note_id"]
    counters: Dict[int, Dict[str, str | Counter[Any]]] = {
        cui_index: {"name": "cui_counter", "counter": Counter()},
        term_index: {"name": "term_counter", "counter": Counter()},
        similarity_index: {"name": "similarity_counter", "counter": Counter()},
        ngram_index: {"name": "ngram_counter", "counter": Counter()},
        semantic_type_index: {"name": "semantic_type_counter", "counter": Counter()},
        note_id_index: {"name": "note_id_counter", "counter": Counter()},
    }

    header_index_list: List[int] = [header.index(h) for h in header]
    for row in rows:
        current = lookup
        for entry_index in header_index_list:
            if entry_index in counters:
                value = row[entry_index]
                _counter = counters[entry_index]["counter"]
                _counter[value] = _counter[value] + 1  # type: ignore

        for i, key in enumerate(selected_headers):
            value = row[header.index(key)]
            if i == len(selected_headers) - 1:
                # At the deepest level, create a dict of unused headers
                unused_dict = {h: row[header.index(h)] for h in unused_headers}
                current.setdefault(value, []).append(unused_dict)
            else:
                current = current.setdefault(value, {})
    return lookup, cast(
        Dict[str, Counter[Any]], {v["name"]: v["counter"] for k, v in counters.items()}
    )


def initialize_paths(project_name: str) -> Tuple[Path, Path]:

    def initialize_csv_to_lookup_root():
        csv_to_lookup_root = Path("/output/csv_to_dict_lookup")
        csv_to_lookup_root.mkdir(parents=True, exist_ok=True)
        return csv_to_lookup_root

    def initialize_config_output_path(csv_to_lookup_root):
        config_output_path: Path = csv_to_lookup_root / "config" / project_name
        config_output_path.mkdir(parents=True, exist_ok=True)
        return config_output_path

    def initialize_lookup_output_path(csv_to_lookup_root):
        lookup_output_path: Path = csv_to_lookup_root / "lookup" / project_name
        lookup_output_path.mkdir(parents=True, exist_ok=True)
        return lookup_output_path

    csv_to_lookup_root: Path = initialize_csv_to_lookup_root()
    config_output_path: Path = initialize_config_output_path(csv_to_lookup_root)
    lookup_output_path: Path = initialize_lookup_output_path(csv_to_lookup_root)
    return config_output_path, lookup_output_path


def persist_config(config_output_path, selected_headers, unused_headers):
    config_dict = {
        "selected_headers": selected_headers,
        "unused_headers": unused_headers,
    }

    config_output_file = make_header_config_path(config_output_path)
    with open(config_output_file, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2)
    logger.info(f"\nSaved header config to: {config_output_file}")


def make_header_config_path(config_output_path):
    return config_output_path / "header_config.json"


def make_nested_lookup_path(lookup_output_path):
    return lookup_output_path / "nested_lookup.json"


def persist_lookup(lookup_output_path, nested_lookup):
    lookup_output_file = make_nested_lookup_path(lookup_output_path)
    with open(lookup_output_file, "w", encoding="utf-8") as f:
        json.dump(nested_lookup, f, indent=2)
    logger.info(f"\nSaved nested lookup to: {lookup_output_file}")


def build_config(
    header: List[HeaderLabel], sample_row, config_output_path, use_current_config
):
    """Add the header fields in order to a list, `available_headers`

    Args:
        header (_type_): _description_
        sample_row (_type_): _description_
        config_output_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    available_headers = header.copy()

    # 3) set selected_headers=[]
    selected_headers = []

    # 4) Menu-driven selection task:
    unused_headers = []

    config_file = make_header_config_path(config_output_path)
    # ask user if they want to use the existing configuration
    if config_file.exists() and config_file.is_file():
        use_existing = use_current_config or (
            input(
                f"\n\nConfig file {config_file} exists.\n\nUse existing configuration? (y/n): "
            )
            .strip()
            .lower()
        )
        if use_current_config or use_existing == "y":
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            selected_headers = config.get("selected_headers", [])
            unused_headers = config.get("unused_headers", [])
            return selected_headers, unused_headers

    # build a new configuration
    while available_headers or selected_headers:
        print("\nAvailable headers:")
        for idx, h in enumerate(available_headers):
            # Find the first non-empty example value for this header
            col_idx = header.index(h)
            example = ""
            example = sample_row[col_idx].strip()
            print(f"{idx + 1}. {h} (e.g. {example})")
        if selected_headers:
            colored = [
                f"{ASCII_COLORS[i % len(ASCII_COLORS)]}{h}{RESET_COLOR}"
                for i, h in enumerate(selected_headers)
            ]
            print("Current selection:", " -> ".join(colored))
        sel = input(
            f"Select header for level {len(selected_headers) + 1} (enter number, 'd' for done, or 'u' to undo): "
        )
        if sel.lower() == "d":
            print("Selection done.")
            # Track unused headers
            unused_headers = available_headers.copy()
            break
        if sel.lower() == "u":
            if selected_headers:
                undone = selected_headers.pop()
                available_headers.append(undone)
                print(f"Undid selection: {undone}")
            else:
                print("Nothing to undo.")
            continue
        try:
            sel_idx = int(sel) - 1
            if sel_idx < 0 or sel_idx >= len(available_headers):
                print("Invalid selection. Try again.")
                continue
        except ValueError:
            print("Invalid input. Try again.")
            continue
        selected = available_headers.pop(sel_idx)
        selected_headers.append(selected)
        print(f"Selected: {selected}")

    if unused_headers:
        logger.info("\nUnused headers:", ", ".join(unused_headers))

    persist_config(config_output_path, selected_headers, unused_headers)
    return selected_headers, unused_headers


def get_sample_header_and_data_iter(rows, ngram_to_lower_case: bool, min_char_length=3):
    traversed_rows = []
    sample_row = None
    # the first row is the header
    header = next(rows)
    # for remaining rows, look for a sample row where each field has at least min_char_length characters
    for row in rows:
        if all(len(field.strip()) >= min_char_length for field in row):
            sample_row = row
            break
        else:
            # if skipped, add to traversed rows to pick up later in the iterator
            traversed_rows.append(row)

    ngram_index = header.index("ngram")

    def row_iterator():

        def _row_iter():
            for row in traversed_rows:
                yield row
            yield sample_row
            for row in rows:
                yield row

        for r in _row_iter():
            assert r is not None
            if ngram_to_lower_case:
                r[ngram_index] = r[ngram_index].lower()
            yield r

    return sample_row, header, row_iterator()


def pretty_print_nested_lookup(d, indent=0):

    if indent == 0:
        logger.info("\nNested dictionary lookup structure:")

    spacing = " " * indent
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                print(f"{spacing}{repr(k)}:")
                pretty_print_nested_lookup(v, indent + 4)
            else:
                print(f"{spacing}{repr(k)}:{repr(v)},")
    elif isinstance(d, list):
        for item in d:
            pretty_print_nested_lookup(item, indent + 4)
    else:
        print(f"{spacing}{repr(d)}")


def load_reader(reader_source, delimeter):
    """Load the file into a CSV reader

    Args:
        reader_source (_type_): _description_
        delimeter (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        file_exists = Path(reader_source).exists()
    except OSError as e:
        file_exists = False

    if file_exists:
        with open(reader_source, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=delimeter)
    else:
        reader = csv.reader(io.StringIO(reader_source.strip()), delimiter=delimeter)
    return reader


def calculate_metrics(
    lookup_output_path,
    header_index_map: Dict[HeaderLabel, int],
    counter: Dict[str, Counter[Any]],
):
    
    # counters: Dict[int, Dict[str, str | Counter[Any]]] = {
    #     cui_index: {"name": "cui_counter", "counter": Counter()},
    #     term_index: {"name": "term_counter", "counter": Counter()},
    #     similarity_index: {"name": "similarity_counter", "counter": Counter()},
    #     ngram_index: {"name": "ngram_counter", "counter": Counter()},
    #     semantic_type_index: {"name": "semantic_type_counter", "counter": Counter()},
    #     note_id_index: {"name": "note_id_counter", "counter": Counter()},
    # }
    
    # notes
    note_counter = counter['note_id_counter']
    num_notes = len(set(note_counter.keys()))

    # cuis
    cui_counter = counter['cui_counter']
    num_cuis = len(set(cui_counter.keys()))

    # terms
    term_counter = counter['term_counter']
    num_terms = len(set(term_counter.keys()))

    # ngrames
    ngram_counter = counter['ngram_counter']
    num_ngrams = len(set(ngram_counter.keys()))

    # semantic types
    semantic_type_counter = counter['semantic_type_counter']
    num_semantic_types = len(set(semantic_type_counter.keys()))

    # similarities
    similarity_counter = counter['similarity_counter']
    num_similarities = len(set(similarity_counter.keys()))

    lookup_file = make_nested_lookup_path(lookup_output_path)

    if not lookup_file.exists():
        logger.error(f"Lookup file not found: {lookup_file}")
        return

    with open(lookup_file, "r", encoding="utf-8") as f:
        nested_lookup = json.load(f)

    logger.info(f"Loaded nested lookup from: {lookup_file}")


def create_header_index_map(
    quickumls_header_values, header: List[HeaderLabel]
) -> Dict[HeaderLabel, int]:
    header_index_map: Dict[HeaderLabel, int] = {
        cast(HeaderLabel, val): int(header.index(val))
        for i, val in enumerate(quickumls_header_values)
    }
    logger.info(f"Header index map: {header_index_map}")
    return header_index_map
