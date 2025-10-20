# QuickUMLS Processor Config Directory

This directory contains configuration files and helper modules for customizing the behavior of the QuickUMLS matcher within the NRE pipeline.

## Configuration Files

### Default Configuration Files

- **default_cosine.yml**
- **default_jaccard.yml**
- **default_levenshtein.yml**

Each YAML file provides default settings for a specific similarity metric. Common configuration keys include:

- `threshold`: Similarity threshold (default: 0.8)
- `similarity_name`: Name of the similarity metric (cosine, jaccard, levenshtein)
- `window`: Number of tokens in the matching window (default: 5)
- `min_match_length`: Minimum length of a match (default: 3)
- `ignore_syntax`: Whether to ignore syntax filtering (default: false)
- `best_match`: Return only the best match per span (default: true)
- `verbose`: Enable verbose logging (default: false)

- **semantic_types.yml**
  - Maps UMLS semantic type codes (e.g., T047, T121) to human-readable descriptions (e.g., Disease or Syndrome, Pharmacologic Substance).

### Custom Configuration Files

You can define a custome config file for use with QuickUMLS, either to adjust existing values or add permitted semantic types.

The following example for `custom_cosine.yml` changes the value for `threshold` as well as adds a list of permitted semantic types, `accepted_semtypes`.

```yml
threshold: 0.7
similarity_name: cosine
window: 5
min_match_length: 3
ignore_syntax: false
best_match: true
verbose: false
accepted_semtypes: [
    "T047",
    "T121",
    "T123"
]
```



## Python Modules

- **config_loader.py**
  - Provides the `QuickUMLSConfig` dataclass for structured configuration.
  - Functions:
    - `load_default_config(metric)`: Loads the default YAML config for the given metric, or, 
    - `get_quickumls_config(config_param, quick_umls_parameters=None)`: Returns the default configuration if the `config_param` is a metric or a custom configuration if `config_param` is a file path.  Optionally, it can override default settings with user-provided parameters.

- **semantic_type_selection.py**
  - Contains the `SemanticTypeSelection` class (currently a stub for future logic related to semantic type filtering or selection).

## Usage

The configuration files and loader module allow you to easily customize QuickUMLS matching behavior by editing YAML files or providing parameters programmatically.

---

For more details, see the docstrings in `config_loader.py` and the comments in each YAML file.
