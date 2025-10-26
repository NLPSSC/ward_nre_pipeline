import os
import pytest
from pathlib import Path
from nre_pipeline.common.env_vars._env_values_manager import EnvValues
from nre_pipeline.converter.data.models.routes._corpus_route import CorpusRoute

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # Ensure environment is clean before each test
    keys = [
        "PROJECT_NAME", "INPUT_ROOT_PATH", "OUTPUT_ROOT_PATH", "TEST_DATA_ROOT_PATH",
        "QUICKUMLS_PATH", "SMALL_CORPUS_PATH", "MEDIUM_CORPUS_PATH", "LARGE_CORPUS_PATH",
        "DEV_UMLS_KEY_PATH", "BATCH_ID_SQLITE_DB_NAME", "DOCUMENT_BATCH_SIZE",
        "INQUEUE_MAX_DOCBATCH_COUNT", "OUTQUEUE_MAX_DOCBATCH_COUNT",
        "NUMBER_DOCS_TO_WRITE_BEFORE_YIELD", "NUMBER_STARTING_PROCESSORS",
        "NUMBER_DOCS_TO_READ_BEFORE_YIELD", "VERBOSE_READER", "LOG_LEVEL"
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)
    yield

@pytest.fixture
def monkeypatch_input_root(monkeypatch):
    monkeypatch.setenv("INPUT_ROOT_PATH", "/input")
    return monkeypatch


def test_get_project_name(monkeypatch):
    monkeypatch.setenv("PROJECT_NAME", "NREPipeline")
    assert EnvValues.get_project_name() == "NREPipeline"

def test_get_input_root(monkeypatch):
    monkeypatch.setenv("INPUT_ROOT_PATH", "/input")
    assert EnvValues.get_input_root() == Path("/input")

def test_get_output_root(monkeypatch):
    monkeypatch.setenv("OUTPUT_ROOT_PATH", "/output")
    assert EnvValues.get_output_root() == Path("/output")

def test_get_test_data_root(monkeypatch):
    monkeypatch.setenv("TEST_DATA_ROOT_PATH", "/test_data")
    assert EnvValues.get_test_data_root() == Path("/test_data")

def test_get_quickumls_path(monkeypatch):
    monkeypatch.setenv("QUICKUMLS_PATH", "/quickumls")
    assert EnvValues.get_quickumls_path() == Path("/quickumls")


def test_get_small_corpus_route(monkeypatch_input_root):
    monkeypatch_input_root.setenv("SMALL_CORPUS_PATH", "/corpus/small")
    route = EnvValues.get_small_corpus_route()
    assert isinstance(route, CorpusRoute)
    assert route.name == "small corpus"
    assert str(route.route_path) == "/input/corpus/small"

def test_get_medium_corpus_route(monkeypatch_input_root):
    monkeypatch_input_root.setenv("MEDIUM_CORPUS_PATH", "/corpus/medium")
    route = EnvValues.get_medium_corpus_route()
    assert isinstance(route, CorpusRoute)
    assert route.name == "medium corpus"
    assert str(route.route_path) == "/input/corpus/medium"

def test_get_large_corpus_route(monkeypatch_input_root):
    monkeypatch_input_root.setenv("LARGE_CORPUS_PATH", "/corpus/large")
    route = EnvValues.get_large_corpus_route()
    assert isinstance(route, CorpusRoute)
    assert route.name == "large corpus"
    assert str(route.route_path) == "/input/corpus/large"

def test_get_dev_umls_key_path(monkeypatch):
    monkeypatch.setenv("DEV_UMLS_KEY_PATH", "/dev/key")
    assert EnvValues.get_dev_umls_key_path() == Path("/dev/key")

def test_get_batch_id_sqlite_db_name(monkeypatch):
    monkeypatch.setenv("BATCH_ID_SQLITE_DB_NAME", "/db/batch.sqlite")
    assert EnvValues.get_batch_id_sqlite_db_name() == Path("/db/batch.sqlite")

def test_get_document_batch_size(monkeypatch):
    monkeypatch.setenv("DOCUMENT_BATCH_SIZE", "42")
    assert EnvValues.get_document_batch_size() == 42

def test_get_inqueue_max_docbatch_count(monkeypatch):
    monkeypatch.setenv("INQUEUE_MAX_DOCBATCH_COUNT", "10")
    assert EnvValues.get_inqueue_max_docbatch_count() == 10

def test_get_outqueue_max_docbatch_count(monkeypatch):
    monkeypatch.setenv("OUTQUEUE_MAX_DOCBATCH_COUNT", "20")
    assert EnvValues.get_outqueue_max_docbatch_count() == 20

def test_get_number_docs_to_write_before_yield(monkeypatch):
    monkeypatch.setenv("NUMBER_DOCS_TO_WRITE_BEFORE_YIELD", "5")
    assert EnvValues.get_number_docs_to_write_before_yield() == 5

def test_get_number_starting_processors(monkeypatch):
    monkeypatch.setenv("NUMBER_STARTING_PROCESSORS", "3")
    assert EnvValues.get_number_starting_processors() == 3

def test_get_number_docs_to_read_before_yield(monkeypatch):
    monkeypatch.setenv("NUMBER_DOCS_TO_READ_BEFORE_YIELD", "7")
    assert EnvValues.get_number_docs_to_read_before_yield() == 7

def test_get_verbose_reader(monkeypatch):
    monkeypatch.setenv("VERBOSE_READER", "True")
    assert EnvValues.get_verbose_reader() is True

def test_get_log_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    assert EnvValues.get_log_level() == "DEBUG"

def test_get_log_level_default(monkeypatch):
    # LOG_LEVEL not set, should default to "INFO"
    assert EnvValues.get_log_level() == "INFO"