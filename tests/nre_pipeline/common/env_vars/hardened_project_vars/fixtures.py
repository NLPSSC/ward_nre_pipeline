import os
import pytest
from pathlib import Path
from nre_pipeline.common.env_vars._env_values_manager import EnvValues  # type: ignore
from nre_pipeline.converter.data.models.routes._corpus_route import CorpusRoute  # type: ignore


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # Ensure environment is clean before each test
    keys = [
        "PROJECT_NAME",
        "INPUT_ROOT_PATH",
        "OUTPUT_ROOT_PATH",
        "TEST_DATA_ROOT_PATH",
        "QUICKUMLS_PATH",
        "SMALL_CORPUS_PATH",
        "MEDIUM_CORPUS_PATH",
        "LARGE_CORPUS_PATH",
        "DEV_UMLS_KEY_PATH",
        "BATCH_ID_SQLITE_DB_NAME",
        "DOCUMENT_BATCH_SIZE",
        "INQUEUE_MAX_DOCBATCH_COUNT",
        "OUTQUEUE_MAX_DOCBATCH_COUNT",
        "NUMBER_DOCS_TO_WRITE_BEFORE_YIELD",
        "NUMBER_STARTING_PROCESSORS",
        "NUMBER_DOCS_TO_READ_BEFORE_YIELD",
        "VERBOSE_READER",
        "LOG_LEVEL",
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture
def monkeypatch_input_root(monkeypatch):
    monkeypatch.setenv("INPUT_ROOT_PATH", "/input")
    return monkeypatch