## Quick purpose

This repository implements a small FastAPI service that converts text documents to images using the Genalog DocumentGenerator. The instructions below highlight the concrete, discoverable patterns and workflows an AI coding agent should follow when making changes.

## Big picture (what to know first)

- Main HTTP surface: `src/api/main.py` exposes three endpoints: `/` (info), `/health`, `/convert-text` and `/convert-file`.
- `/convert-text` returns a Pydantic response (base64-encoded image). `/convert-file` returns binary image data with a `Content-Disposition` attachment.
- Document generation is performed by Genalog's `DocumentGenerator` (imported as `from genalog.generation.document import DocumentGenerator`) and its `create_img_from_text(...)` method, which returns a list of filesystem paths to generated images.
- Temporary files and directories are used for input and outputs (see `tempfile.NamedTemporaryFile` and `tempfile.TemporaryDirectory`). Cleanup (unlinking the temp text file) is done in a finally block — preserve this behavior.

## Key files to read / edit

- `src/api/main.py` — primary app implementation, Pydantic models, and HTTP handlers.
- `src/__main__.py` — simple entrypoint that runs uvicorn for local development.
- `src/test_client.py` — example client showing request/response shape and how to decode/save result.
- `requirements.txt` — runtime/test dependencies (FastAPI, uvicorn, genalog, pillow, pytest).
- `tests/` — comprehensive unit + integration tests showing mocking patterns and expected behavior. Read tests to learn accepted edge cases.

## How to run (developer workflow)

- Create a venv and install deps:

  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt

- Run the API (dev with auto-reload):

  # from repository root
  python src/__main__.py

  # or directly with uvicorn
  uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

- Test manually with the example client:

  python src/test_client.py

- Run automated tests:

  pytest

If you change public behavior (endpoints, models, status codes), update tests under `tests/` accordingly.

## Project-specific conventions & patterns

- API model defaults live on Pydantic models in `src/api/main.py`. If you alter a default, update tests that assert those defaults (see `tests/test_models.py`).
- Conversion flow: generate a temporary `.txt`, call `create_img_from_text(...)`, read the first returned path, encode to base64 (for `/convert-text`) or return bytes (for `/convert-file`). Preserve the two-return styles.
- Error handling: handlers raise `fastapi.HTTPException` with explicit status codes and descriptive `detail` strings. Tests check for these exact details in many cases — keep messages stable when possible.

## Testing & mocking details (important for AI changes)

- Tests mock Genalog to avoid heavy generation. Look at `tests/conftest.py` for fixtures — they patch DocumentGenerator using a fully-qualified import string. Two common patch targets appear across the tests:
  - `api.main.DocumentGenerator` — patch this if you import `DocumentGenerator` directly in `src/api/main.py` (recommended when editing that file).
  - `src.genalog_api.api.main.DocumentGenerator` — some tests use this path. If you refactor modules or package names, update tests and patch targets accordingly.
- Tests also heavily mock filesystem/IO: `tempfile.NamedTemporaryFile`, `tempfile.TemporaryDirectory`, `builtins.open`, and `pathlib.Path.exists` / `unlink`. When adding file I/O, mirror these seams so tests can stub them.

## Integration points & external dependencies

- genalog (DocumentGenerator) — the core external dependency. Its API used here: `create_img_from_text(text, output_folder, target_image_width, target_image_height)` returning paths. Changes to call shape must be reflected in tests.
- Pillow determines supported output formats; `image_format` values are passed through to response headers / model fields.
- Uvicorn runs the ASGI app in development. CI/test environments may use pytest + TestClient (no running server required).

## Small guidance for code edits

- Preserve public API contracts: endpoint paths, response JSON shape for `/convert-text`, and binary behavior for `/convert-file`.
- Keep temp-file cleanup in finally blocks; tests assert unlink is called.
- When adding new features that touch generation, add a unit test that mocks `DocumentGenerator.create_img_from_text` and asserts its call args.
- If you move modules or rename packages, update test patch targets in `tests/conftest.py` and all `patch(...)` calls.

## Quick checklist for AI PRs

1. Run unit tests (pytest) and fix failing tests locally.
2. Inspect `tests/` to mirror mocking patterns for external Genalog calls and filesystem interactions.
3. Keep HTTP error messages and status codes stable or update tests to expect new strings.
4. Update `README.md` or `src/test_client.py` examples if the runtime command or API contract changes.

---
If any behavior or external API is unclear (for example, exact Genalog call args or the desired format of attachments), ask for a short clarification and point to the tests or `src/api/main.py` lines you inspected.
