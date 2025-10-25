import io
import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast
from loguru import logger

from nre_pipeline.converter.data.initialize_paths import get_project_lookup_output_path

from ..models.consts import HeaderLabel
from ..models.quickumls_counters import QuickUMLSCounters

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
) -> Tuple[Dict[Any, Any], QuickUMLSCounters]:
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
    counters: QuickUMLSCounters = QuickUMLSCounters()

    header_index_list: List[int] = [header.index(h) for h in header]
    for row in rows:
        current = lookup
        for entry_index in header_index_list:
            header_field = header[entry_index]
            value = row[entry_index]

            counters.increment(header_field, value)

        for i, key in enumerate(selected_headers):
            value = row[header.index(key)]
            if i == len(selected_headers) - 1:
                # At the deepest level, create a dict of unused headers
                unused_dict = {h: row[header.index(h)] for h in unused_headers}
                current.setdefault(value, []).append(unused_dict)
            else:
                current = current.setdefault(value, {})
    return lookup, counters


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


def make_nested_lookup_path():
    return get_project_lookup_output_path() / "nested_lookup.json"


def persist_lookup(nested_lookup: Dict[str, Any]):
    lookup_output_file = make_nested_lookup_path()
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


def create_header_index_map(
    quickumls_header_values, header: List[HeaderLabel]
) -> Dict[HeaderLabel, int]:
    header_index_map: Dict[HeaderLabel, int] = {
        cast(HeaderLabel, val): int(header.index(val))
        for i, val in enumerate(quickumls_header_values)
    }
    logger.info(f"Header index map: {header_index_map}")
    return header_index_map
