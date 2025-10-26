import os
from pathlib import Path
from typing import Any, Callable, Literal, Optional, TypeAlias, TypeVar, Union

from overrides import override

from nre_pipeline.converter.data.models.routes._corpus_route import CorpusRoute

RequirementType: TypeAlias = Literal["EnvVar Missing", "EnvVar Validation Method Failure"]

class EnvValues:

    @staticmethod
    def get(key: str, required: Union[bool, Callable[[Any], bool]] = True) -> Optional[str]:
        requirement: Literal["EnvVar Missing", "EnvVar Validation Method Failure"]
        if isinstance(required, bool):
            requirement = "EnvVar Missing"
            required = lambda _: True
        else:
            requirement = "EnvVar Validation Method Failure"
        env_var_val: Optional[str] = os.getenv(key, None)
        if env_var_val is None:
            if required(env_var_val):
                raise EnvironmentError(f"Environment variable '{key}' is not valid ({requirement})")
        return env_var_val

    @staticmethod
    @override
    def get(key: str, required: bool = False) -> Optional[str]:
        env_var_val: Optional[str] = os.getenv(key, None)
        return env_var_val
    
    @staticmethod
    @override
    def get(key: str, required: bool = True) -> str:
        env_var_val: Optional[str] = EnvValues.get(key, False)
        if env_var_val is None:
            raise EnvironmentError(f"Environment variable '{key}' is not valid (EnvVar Missing)")
        assert env_var_val is not None
        return env_var_val

    ###############################################################################
    # The project root name, used throughout the project space
    ###############################################################################
    
    @staticmethod
    def get_project_name() -> str:
        return EnvValues.get("PROJECT_NAME")

    ###############################################################################
    # Define root folders for input, output, and test data
    ###############################################################################
    
    @staticmethod
    def get_input_root() -> Path:
        val = EnvValues.get("INPUT_ROOT_PATH")
        return Path(val)

    @staticmethod
    def get_output_root() -> Path:
        val: Optional[str] = EnvValues.get("OUTPUT_ROOT_PATH")
        return Path(val)

    @staticmethod
    def get_test_data_root() -> Path:
        val = EnvValues.get("TEST_DATA_ROOT_PATH")
        return Path(val)

    ###############################################################################
    #
    ###############################################################################

    @staticmethod
    def get_quickumls_path() -> Path:
        val = EnvValues.get("QUICKUMLS_PATH")
        return Path(val)

    @staticmethod
    def get_small_corpus_route() -> CorpusRoute:
        val = EnvValues.get("SMALL_CORPUS_PATH")
        return CorpusRoute(val)

    @staticmethod
    def get_medium_corpus_route() -> CorpusRoute:
        val = EnvValues.get("MEDIUM_CORPUS_PATH")
        return CorpusRoute(val)

    @staticmethod
    def get_large_corpus_route() -> CorpusRoute:
        val = EnvValues.get("LARGE_CORPUS_PATH")
        return CorpusRoute(val)

    @staticmethod
    def get_dev_umls_key_path() -> Path:
        val = EnvValues.get("DEV_UMLS_KEY_PATH")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'DEV_UMLS_KEY_PATH' is not set"
            )
        return Path(val)

    @staticmethod
    def get_batch_id_sqlite_db_name() -> Path:
        val = EnvValues.get("BATCH_ID_SQLITE_DB_NAME")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'BATCH_ID_SQLITE_DB_NAME' is not set"
            )
        return Path(val)

    @staticmethod
    def get_document_batch_size() -> int:
        val = EnvValues.get("DOCUMENT_BATCH_SIZE")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'DOCUMENT_BATCH_SIZE' is not set"
            )
        return int(val)

    @staticmethod
    def get_inqueue_max_docbatch_count() -> int:
        val = EnvValues.get("INQUEUE_MAX_DOCBATCH_COUNT")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'INQUEUE_MAX_DOCBATCH_COUNT' is not set"
            )
        return int(val)

    @staticmethod
    def get_outqueue_max_docbatch_count() -> int:
        val = EnvValues.get("OUTQUEUE_MAX_DOCBATCH_COUNT")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'OUTQUEUE_MAX_DOCBATCH_COUNT' is not set"
            )
        return int(val)

    @staticmethod
    def get_number_docs_to_write_before_yield() -> int:
        val = EnvValues.get("NUMBER_DOCS_TO_WRITE_BEFORE_YIELD")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'NUMBER_DOCS_TO_WRITE_BEFORE_YIELD' is not set"
            )
        return int(val)

    @staticmethod
    def get_number_starting_processors() -> int:
        val = EnvValues.get("NUMBER_STARTING_PROCESSORS")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'NUMBER_STARTING_PROCESSORS' is not set"
            )
        return int(val)

    @staticmethod
    def get_number_docs_to_read_before_yield() -> int:
        val = EnvValues.get("NUMBER_DOCS_TO_READ_BEFORE_YIELD")
        if val is None:
            raise EnvironmentError(
                "Environment variable 'NUMBER_DOCS_TO_READ_BEFORE_YIELD' is not set"
            )
        return int(val)

    @staticmethod
    def get_verbose_reader() -> str:
        val = EnvValues.get("VERBOSE_READER")
        if val is None:
            raise EnvironmentError("Environment variable 'VERBOSE_READER' is not set")
        return val

    @staticmethod
    def get_log_level() -> str:
        val = EnvValues.get("LOG_LEVEL")
        if val is None:
            raise EnvironmentError("Environment variable 'LOG_LEVEL' is not set")
        return val
