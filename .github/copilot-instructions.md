# Copilot Instructions for NRE Pipeline

## Big Picture Architecture

- The repository contains two main components:
  - **Genalog API Service** (`src/genalog_api`): FastAPI service for converting text to images using Genalog's `DocumentGenerator`.
  - **NRE Pipeline** (`src/nre_pipeline`): Core pipeline for processing non-routine events, with modular reader, processor, and writer components.
- Data flows from readers (e.g., `FileSystemReader`) through processors (e.g., `NoOpProcessor`, `QuickUMLS`) to writers (e.g., `SQLiteNLPWriter`).
- Service boundaries are clear: Genalog API is for text-to-image, NRE Pipeline is for event processing and NLP.

## Developer Workflows

- **Environment Setup:**
  - Use Conda/mamba for environment management. See `Makefile.nre_pipeline.mk` and `environment.yml`.
  - Activate environments before running Python commands.
- **Build & Install:**
  - Run `make install` to build and install dependencies for NRE Pipeline.
  - For Genalog API, use `mamba create -p .\envs\genalog_api_env -f src/genalog_api/environment.yml`.
- **Testing:**
  - Run `make test` or `pytest` in the appropriate environment.
  - Genalog API tests mock heavy dependencies and file I/O; see `tests/conftest.py` for patching patterns.
  - NRE Pipeline tests are in `src/nre_pipeline/tests/` and use unittest.
- **Debugging:**
  - VS Code launch configs in `.vscode/launch.json` for debugging pipeline and API modules.
  - Use verbose logging via command-line args or launch configs.
- **Git Bundle/Upload:**
  - Use the `git Bundle/Upload NRE Pipeline` task or run `scripts\bundle\push_gitbundle.bat` to create and upload git bundles to remote servers.

## Project-Specific Conventions

- **Temporary files**: Always clean up temp files in `finally` blocks; tests assert this behavior.
- **API contracts**: Keep endpoint paths, response shapes, and error messages stable. Update tests if changed.
- **Mocking**: Patch external dependencies and file I/O in tests. Update patch targets if refactoring.
- **Batch size and file extensions**: Readers and processors often use batch processing and filter by file extension (see `FileSystemReader`).

## Integration Points & External Dependencies

- **Genalog**: Used for document generation in API.
- **QuickUMLS**: Used in NRE Pipeline for medical NLP.
- **Pillow**: Image processing for API.
- **SQLite**: Used by writers for storing NLP results.

## Key Files & Directories

- `src/genalog_api/api/main.py`: FastAPI endpoints and models.
- `src/genalog_api/tests/`: API tests and mocking patterns.
- `src/nre_pipeline/src/main.py`: NRE Pipeline main logic.
- `src/nre_pipeline/tests/`: Pipeline tests.
- `src/nre_pipeline/src/Makefile.nre_pipeline.mk`: Build and environment commands.
- `.vscode/launch.json`: Debugging configs.
- `scripts/bundle/push_gitbundle.bat`: Git bundle upload workflow.

## Checklist for AI Agents

1. Run all tests after changes.
2. Mirror existing mocking and patching patterns in new tests.
3. Update tests and examples if public API or CLI changes.
4. Clean up temp files and update tests to assert cleanup.
5. Ask for clarification if any workflow, integration, or contract is unclear.

---

If any section is unclear or incomplete, please provide feedback so instructions can be improved.
