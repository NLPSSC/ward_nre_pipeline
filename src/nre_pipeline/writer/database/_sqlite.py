import json
import os
from typing import Any, Callable, Dict, cast
from functools import lru_cache

from html5lib import serialize
from loguru import logger

from nre_pipeline.models import NLPResult
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.writer import NLPResultWriter
from nre_pipeline.writer.common import DBNLPResultWriter
from nre_pipeline.writer.database import (
    DatabaseExecutionContext,
    SQLiteExecutionContext,
)


def convert_python_type_to_sqlite_type(item) -> str:
    python_type = item.value_type
    if python_type is int:
        return "INTEGER"
    elif python_type is float:
        return "REAL"
    elif python_type is str:
        return "TEXT"
    elif python_type is bool:
        return "BOOLEAN"
    elif python_type is set:
        return "TEXT"
    elif python_type is list:
        return "TEXT"
    elif python_type is dict:
        return "TEXT"
    else:
        raise ValueError(f"Unsupported Python type: {python_type}")

def serialize_item(item: NLPResultItem) -> Any:
    if item.value_type is set:
        return json.dumps(list(item.value))
    elif item.value_type is list:
        return json.dumps(item.value)
    elif item.value_type is dict:
        return json.dumps(item.value)
    else:
        return item.value


class SQLiteNLPWriter(DBNLPResultWriter):
    """SQLite implementation of the NLP result writer.

    Args:
        DBNLPResultWriter (_type_): _description_
    """

    def __init__(self, db_path: str | None = None):
        self._db_path = self._get_db_path(db_path)
        self._cached_insert_query: str | None = None
        super().__init__()

    def get_create_table_query(self, nlp_result: NLPResult) -> str:
        note_id: str | int = nlp_result.note_id
        additional_columns = ", ".join(
            [
                f"{item.key} {convert_python_type_to_sqlite_type(item)}"
                for item in nlp_result.results
            ]
        )

        if isinstance(note_id, int):
            note_id_type = "INTEGER"
        else:
            note_id_type = "TEXT"

        return f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id {note_id_type},
                {additional_columns}
            )
        """

    def _get_db_path(self, db_path: str | None) -> str:
        _path = db_path or os.getenv("RESULTS_PATH", None)
        if _path is None:
            raise ValueError(
                "Database path must be provided either as an argument or via the RESULTS_PATH environment variable."
            )
        return cast(str, _path)

    def _record(self, nlp_result: NLPResult, context: DatabaseExecutionContext) -> None:
        query = self.get_insert_query(nlp_result)
        insert_params = (
            nlp_result.note_id,
            *[serialize_item(item) for item in nlp_result.results],
        )
        context.insert(query, insert_params)

    def get_insert_query(self, nlp_result) -> str:
        if self._cached_insert_query is not None:
            return self._cached_insert_query
        additional_columns = [item.key for item in nlp_result.results]
        additional_columns_str = ", ".join(additional_columns)
        question_marks = ", ".join(["?"] * len(additional_columns))
        query: str = f"INSERT INTO nlp_results (note_id, {additional_columns_str}) VALUES (?, {question_marks})"
        self._cached_insert_query = query
        return query

    def _get_database_context(self) -> DatabaseExecutionContext:
        return SQLiteExecutionContext(self._db_path)

    def on_transaction_begin(self, context: DatabaseExecutionContext) -> None:
        # logger.debug("Transaction started.")
        pass

    def on_transaction_commit(self, context: DatabaseExecutionContext) -> None:
        # logger.debug("Transaction committed.")
        pass

    def on_transaction_rollback(self, context: DatabaseExecutionContext) -> None:
        logger.debug("Transaction rolled back.")

    @staticmethod
    def create_writer(**kwargs) -> Callable[[], NLPResultWriter]:
        db_path = kwargs.get("db_path", None)
        if db_path is None:
            raise ValueError("Database path must be provided.")
        return lambda: SQLiteNLPWriter(db_path=db_path)

    def writer_details(self) -> Dict[str, Any]:
        return {"database_path": self._db_path}
