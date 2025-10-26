import os
from pathlib import Path
from typing import Any, Callable, Literal, Optional, TypeAlias, TypeVar, Union, cast

from numpy import require
from overrides import override
from loguru import logger
from nre_pipeline.common.env_vars.env_getter import (
    TRequired,
    TValidator,
    get_env,
    get_env_as_bool,
    get_env_as_int,
)
from nre_pipeline.converter.data.models.routes._corpus_route import CorpusRoute

RequirementType: TypeAlias = Literal[
    "EnvVar Missing", "EnvVar Validation Method Failure"
]


class EnvValues:

    # @staticmethod
    # @override
    # def get_env(key: str, required: bool = False) -> Optional[str]:
    #     env_var_val: Optional[str] = os.getenv(key, None)
    #     return env_var_val

    # @staticmethod
    # @override
    # def get(key: str, required: bool = True) -> str:
    #     env_var_val: Optional[str] = get_env(key, False)
    #     if env_var_val is None:
    #         raise EnvironmentError(f"Environment variable '{key}' is not valid (EnvVar Missing)")
    #     assert env_var_val is not None
    #     return env_var_val

    ###############################################################################
    # The project root name, used throughout the project space
    ###############################################################################

    @staticmethod
    def get_project_name() -> str:
        return get_env("PROJECT_NAME", required="exists")

    ###############################################################################
    # Define root folders for input, output, and test data
    ###############################################################################

    @staticmethod
    def get_input_root() -> Path:
        val: str = get_env("INPUT_ROOT_PATH", required="exists")
        return Path(val)

    @staticmethod
    def get_output_root() -> Path:
        val: str = get_env("OUTPUT_ROOT_PATH", required="exists")
        return Path(val)

    @staticmethod
    def get_test_data_root() -> Path:
        val: str = get_env("TEST_DATA_ROOT_PATH", required="exists")
        return Path(val)

    ###############################################################################
    #
    ###############################################################################

    @staticmethod
    def get_quickumls_path() -> Path:
        val: str = get_env("QUICKUMLS_PATH", required="exists")
        return Path(val)

    @staticmethod
    def get_small_corpus_route() -> CorpusRoute:
        val: Optional[str] = get_env("SMALL_CORPUS_PATH")
        return CorpusRoute("small corpus", val)

    @staticmethod
    def get_medium_corpus_route() -> CorpusRoute:
        val: Optional[str] = get_env("MEDIUM_CORPUS_PATH")
        return CorpusRoute("medium corpus", val)

    @staticmethod
    def get_large_corpus_route() -> CorpusRoute:
        val: Optional[str] = get_env("LARGE_CORPUS_PATH")
        return CorpusRoute("large corpus", val)

    @staticmethod
    def get_dev_umls_key_path() -> Path:
        val: str = get_env("DEV_UMLS_KEY_PATH", required="exists")
        return Path(val)

    @staticmethod
    def get_batch_id_sqlite_db_name() -> Path:
        val: str = get_env("BATCH_ID_SQLITE_DB_NAME", required="exists")
        return Path(val)

    @staticmethod
    def get_document_batch_size() -> int:
        return cast(int, get_env_as_int("DOCUMENT_BATCH_SIZE", required="exists"))

    @staticmethod
    def get_inqueue_max_docbatch_count() -> int:
        return cast(
            int,
            get_env_as_int("INQUEUE_MAX_DOCBATCH_COUNT", required="exists"),
        )

    @staticmethod
    def get_outqueue_max_docbatch_count() -> int:
        return cast(
            int,
            get_env_as_int("OUTQUEUE_MAX_DOCBATCH_COUNT", required="exists"),
        )

    @staticmethod
    def get_number_docs_to_write_before_yield() -> int:
        return cast(
            int,
            get_env_as_int("NUMBER_DOCS_TO_WRITE_BEFORE_YIELD", required="exists"),
        )

    @staticmethod
    def get_number_starting_processors() -> int:
        return cast(
            int,
            get_env_as_int("NUMBER_STARTING_PROCESSORS", required="exists"),
        )

    @staticmethod
    def get_number_docs_to_read_before_yield() -> int:
        return cast(
            int,
            get_env_as_int("NUMBER_DOCS_TO_READ_BEFORE_YIELD", required="exists"),
        )

    @staticmethod
    def get_verbose_reader() -> bool:
        return cast(bool, get_env_as_bool("VERBOSE_READER", required="exists"))

    @staticmethod
    def get_log_level() -> str:
        val = get_env("LOG_LEVEL")
        if val is None:
            logger.warning(
                'LOG_LEVEL environment variable not set; defaulting to "INFO"'
            )
            val = "INFO"
        return val
