import os
from pathlib import Path
from typing import Optional

from nre_pipeline.converter.data.models.routes._corpus_route import CorpusRoute


class EnvValues:

    @staticmethod
    def lookup(key) -> Optional[str]:
        return os.getenv(key, None)

    @staticmethod
    def get_project_name() -> str:
        val = EnvValues.lookup("PROJECT_NAME")
        if val is None:
            raise EnvironmentError("Environment variable 'PROJECT_NAME' is not set")
        return val

    @staticmethod
    def get_input_root_path() -> Path:
        val = EnvValues.lookup("INPUT_ROOT_PATH")
        if val is None:
            raise EnvironmentError("Environment variable 'INPUT_ROOT_PATH' is not set")
        return Path(val)

    @staticmethod
    def get_quickumls_path() -> Path:
        val = EnvValues.lookup("QUICKUMLS_PATH")
        if val is None:
            raise EnvironmentError("Environment variable 'QUICKUMLS_PATH' is not set")
        return Path(val)

    @staticmethod
    def get_test_data_path() -> Path:
        val = EnvValues.lookup("TEST_DATA_PATH")
        if val is None:
            raise EnvironmentError("Environment variable 'TEST_DATA_PATH' is not set")
        return Path(val)

    @staticmethod
    def get_small_corpus_route() -> CorpusRoute:
        val = EnvValues.lookup("SMALL_CORPUS_PATH")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'SMALL_CORPUS_PATH' is not set"
            )
        assert val is not None
        return CorpusRoute(val)

    @staticmethod
    def get_medium_corpus_route() -> CorpusRoute:
        val = EnvValues.lookup("MEDIUM_CORPUS_PATH")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'MEDIUM_CORPUS_PATH' is not set"
            )
        return val

    @staticmethod
    def get_large_corpus_route() -> CorpusRoute:
        val = EnvValues.lookup("LARGE_CORPUS_PATH")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'LARGE_CORPUS_PATH' is not set"
            )
        return val

    @staticmethod
    def get_dev_umls_key_path() -> Path:
        val = EnvValues.lookup("DEV_UMLS_KEY_PATH")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'DEV_UMLS_KEY_PATH' is not set"
            )
        return Path(val)

    @staticmethod
    def get_batch_id_sqlite_db_name() -> Path:
        val = EnvValues.lookup("BATCH_ID_SQLITE_DB_NAME")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'BATCH_ID_SQLITE_DB_NAME' is not set"
            )
        return Path(val)

    @staticmethod
    def get_document_batch_size() -> int:
        val = EnvValues.lookup("DOCUMENT_BATCH_SIZE")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'DOCUMENT_BATCH_SIZE' is not set"
            )
        return int(val)

    @staticmethod
    def get_inqueue_max_docbatch_count() -> int:
        val = EnvValues.lookup("INQUEUE_MAX_DOCBATCH_COUNT")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'INQUEUE_MAX_DOCBATCH_COUNT' is not set"
            )
        return int(val)

    @staticmethod
    def get_outqueue_max_docbatch_count() -> int:
        val = EnvValues.lookup("OUTQUEUE_MAX_DOCBATCH_COUNT")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'OUTQUEUE_MAX_DOCBATCH_COUNT' is not set"
            )
        return int(val)

    @staticmethod
    def get_number_docs_to_write_before_yield() -> int:
        val = EnvValues.lookup("NUMBER_DOCS_TO_WRITE_BEFORE_YIELD")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'NUMBER_DOCS_TO_WRITE_BEFORE_YIELD' is not set"
            )
        return int(val)

    @staticmethod
    def get_number_starting_processors() -> int:
        val = EnvValues.lookup("NUMBER_STARTING_PROCESSORS")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'NUMBER_STARTING_PROCESSORS' is not set"
            )
        return int(val)

    @staticmethod
    def get_number_docs_to_read_before_yield() -> int:
        val = EnvValues.lookup("NUMBER_DOCS_TO_READ_BEFORE_YIELD")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'NUMBER_DOCS_TO_READ_BEFORE_YIELD' is not set"
            )
        return int(val)

    @staticmethod
    def get_verbose_reader() -> str:
        val = EnvValues.lookup("VERBOSE_READER")
        if val is None:
            raise EnvironmentError("Environment variable 'VERBOSE_READER' is not set")
        return val

    @staticmethod
    def get_log_level() -> str:
        val = EnvValues.lookup("LOG_LEVEL")
        if val is None:
            raise EnvironmentError("Environment variable 'LOG_LEVEL' is not set")
        return val

    @staticmethod
    def get_output_root() -> Path:
        output_root: Optional[str] = EnvValues.lookup("OUTPUT_ROOT_PATH")
        if output_root is None:
            raise EnvironmentError("Environment variable 'OUTPUT_ROOT_PATH' is not set")
        return Path(output_root)
