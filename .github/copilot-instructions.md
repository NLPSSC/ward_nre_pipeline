# Copilot Instructions for ward_nre_pipeline

## Project Overview

- This repository contains two main components:
  - **nre_pipeline**: Processes healthcare Non-Routine Events (NRE) for analysis. CLI and Python module entry points are in `nre_pipeline/src/__main__.py` and `nre_pipeline/src/main.py`.
  - **genalog_api**: RESTful API for converting text documents to images using Genalog. Entrypoints are `genalog_api/src/__main__.py` and `genalog_api/src/start_api.bat`.

## Architecture & Data Flow

- **nre_pipeline**: Modular structure with subfolders for models, pipeline management, processors, readers, and writers. Data flows from readers → processors → writers.
- **genalog_api**: FastAPI-based service. API endpoints defined in `genalog_api/src/api/main.py`. Models in `genalog_api/src/api/models/`. Tests in `genalog_api/tests/`.

## Developer Workflows

- **Environment Setup**:
  - Use Conda/Mamba for reproducible environments. Example:
    ```shell
    mamba create -p envs\nre_pipeline python=3.11
    mamba install anaconda::medspacy_quickumls conda-forge::loguru
    python -m spacy download en_core_web_sm
    python -m quickumls.install <UMLS_META_PATH> <QUICKUMLS_PATH>
    ```
  - For Genalog API:
    ```shell
    mamba create -p .\envs\genalog_api_env -f .\src\genalog_api\environment.yml
    mamba activate .\envs\genalog_api_env
    pip install -r requirements.txt
    ```
- **Build & Run**:
  - nre_pipeline: `python -m nre_pipeline --help` or use CLI entrypoint.
  - genalog_api: `python __main__.py` or `start_api.bat` (Windows).
- **Testing**:
  - nre_pipeline: `python -m pytest tests/`
  - genalog_api: `pytest tests/genalog_api/ --cov=src.genalog_api`
- **Formatting**: Use `black src/ tests/` for code style.

## Project-Specific Patterns

- **nre_pipeline**:
  - Processors follow a mixin pattern for interruptibility (`interruptible_mixin.py`).
  - QuickUMLS integration requires manual installation and resource setup.
  - Tests are in `nre_pipeline/src/tests/` and cover pipeline, processor, reader, and writer modules.
- **genalog_api**:
  - API endpoints are tested for success, error, and edge cases. See `tests/README.md` for coverage details.
  - Pydantic models are used for request/response validation.
  - Mocking and fixtures are centralized in `conftest.py`.

## Integration Points

- **QuickUMLS**: Requires UMLS resources and custom install command.
- **Genalog**: Used for text-to-image conversion; API exposes endpoints for direct text and file upload.

## Conventions

- Use batch scripts for Windows-specific tasks (e.g., `start_api.bat`).
- All new modules should include docstrings and type hints.
- Tests should cover error handling and edge cases, not just happy paths.

## Key Files & Directories

- `nre_pipeline/src/__main__.py`, `main.py`: Entrypoints for pipeline.
- `nre_pipeline/src/processor/`: Custom processors, including QuickUMLS.
- `genalog_api/src/api/main.py`: API endpoint definitions.
- `genalog_api/tests/`: Comprehensive test suite.
- `nre_pipeline/.docs/README.md`, `genalog_api/README.md`: Additional setup and usage details.

---

For unclear or incomplete sections, please provide feedback or specify which workflows, patterns, or integrations need further documentation.
