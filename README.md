# NRE Pipeline

Non-Routine Events (NRE) Pipeline for healthcare event processing and analysis.

## Installation

To install the package in development mode:

```bash
pip install -e .
```

To install with development dependencies:

```bash
pip install -e .[dev]
```

## Usage

Run the pipeline using the command line interface:

```bash
nre-pipeline --help
```

Or run it as a Python module:

```bash
python -m nre_pipeline --help
```

## Development

### Project Structure

```
nre_pipeline/
├── src/
│   ├── __main__.py          # CLI entry point
│   └── nre_pipeline/        # Main package
│       ├── __init__.py
│       └── main.py          # Core functionality
├── tests/                   # Unit tests
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Running Tests

```bash
python -m pytest tests/
```

### Code Formatting

```bash
black src/ tests/
```

## License

MIT License


## Notes

- GitHub repo created from local using `gh repo create NLPSSC/ward_nre_pipeline --public --source=. --remote=origin --push`