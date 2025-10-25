import os
import pytest
from pathlib import Path
from nre_pipeline.common.env_vars._env_values_manager import EnvValues


# Helper to set and unset env vars
def set_env(key, value):
    os.environ[key] = value


def unset_env(key):
    if key in os.environ:
        del os.environ[key]


@pytest.mark.parametrize(
    "method,key,value,expected,type_",
    [
        (
            EnvValues.get_input_data_path,
            "INPUT_DATA_PATH",
            "/tmp/input",
            Path("/tmp/input"),
            Path,
        ),
        (
            EnvValues.get_quickumls_path,
            "QUICKUMLS_PATH",
            "/tmp/quickumls",
            Path("/tmp/quickumls"),
            Path,
        ),
        (EnvValues.get_project_name, "PROJECT_NAME", "myproject", "myproject", str),
        (
            EnvValues.get_test_data_path,
            "TEST_DATA_PATH",
            "/tmp/testdata",
            Path("/tmp/testdata"),
            Path,
        ),
        (
            EnvValues.get_dev_umls_key_path,
            "DEV_UMLS_KEY_PATH",
            "/tmp/devkey",
            Path("/tmp/devkey"),
            Path,
        ),
        (
            EnvValues.get_batch_id_sqlite_db_name,
            "BATCH_ID_SQLITE_DB_NAME",
            "/tmp/batch.db",
            Path("/tmp/batch.db"),
            Path,
        ),
        (EnvValues.get_document_batch_size, "DOCUMENT_BATCH_SIZE", "42", 42, int),
        (
            EnvValues.get_inqueue_max_docbatch_count,
            "INQUEUE_MAX_DOCBATCH_COUNT",
            "10",
            10,
            int,
        ),
        (
            EnvValues.get_outqueue_max_docbatch_count,
            "OUTQUEUE_MAX_DOCBATCH_COUNT",
            "20",
            20,
            int,
        ),
        (
            EnvValues.get_NUMBER_DOCS_TO_WRITE_BEFORE_YIELD,
            "NUMBER_DOCS_TO_WRITE_BEFORE_YIELD",
            "5",
            5,
            int,
        ),
        (
            EnvValues.get_NUMBER_STARTING_PROCESSORS,
            "NUMBER_STARTING_PROCESSORS",
            "3",
            3,
            int,
        ),
        (
            EnvValues.get_NUMBER_DOCS_TO_READ_BEFORE_YIELD,
            "NUMBER_DOCS_TO_READ_BEFORE_YIELD",
            "7",
            7,
            int,
        ),
        (EnvValues.get_verbose_reader, "VERBOSE_READER", "true", "true", str),
        (EnvValues.get_log_level, "LOG_LEVEL", "DEBUG", "DEBUG", str),
        (
            EnvValues.get_output_root,
            "RESULTS_PATH",
            "/tmp/results",
            Path("/tmp/results"),
            Path,
        ),
    ],
)
def test_env_value_success(method, key, value, expected, type_):
    set_env(key, value)
    result = method()
    assert result == expected
    assert isinstance(result, type_)
    unset_env(key)


@pytest.mark.parametrize(
    "method,key",
    [
        (EnvValues.get_input_data_path, "INPUT_DATA_PATH"),
        (EnvValues.get_quickumls_path, "QUICKUMLS_PATH"),
        (EnvValues.get_project_name, "PROJECT_NAME"),
        (EnvValues.get_test_data_path, "TEST_DATA_PATH"),
        (EnvValues.get_dev_umls_key_path, "DEV_UMLS_KEY_PATH"),
        (EnvValues.get_batch_id_sqlite_db_name, "BATCH_ID_SQLITE_DB_NAME"),
        (EnvValues.get_document_batch_size, "DOCUMENT_BATCH_SIZE"),
        (EnvValues.get_inqueue_max_docbatch_count, "INQUEUE_MAX_DOCBATCH_COUNT"),
        (EnvValues.get_outqueue_max_docbatch_count, "OUTQUEUE_MAX_DOCBATCH_COUNT"),
        (
            EnvValues.get_NUMBER_DOCS_TO_WRITE_BEFORE_YIELD,
            "NUMBER_DOCS_TO_WRITE_BEFORE_YIELD",
        ),
        (EnvValues.get_NUMBER_STARTING_PROCESSORS, "NUMBER_STARTING_PROCESSORS"),
        (
            EnvValues.get_NUMBER_DOCS_TO_READ_BEFORE_YIELD,
            "NUMBER_DOCS_TO_READ_BEFORE_YIELD",
        ),
        (EnvValues.get_verbose_reader, "VERBOSE_READER"),
        (EnvValues.get_log_level, "LOG_LEVEL"),
        (EnvValues.get_output_root, "RESULTS_PATH"),
    ],
)
def test_env_value_missing(method, key):
    unset_env(key)
    with pytest.raises(EnvironmentError):
        method()
