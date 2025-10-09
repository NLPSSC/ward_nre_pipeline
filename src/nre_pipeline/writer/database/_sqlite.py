import os
from typing import Any, Dict, cast

from loguru import logger

from nre_pipeline.models import NLPResult
from nre_pipeline.writer.database._execution_context import DatabaseExecutionContext
from nre_pipeline.writer.database._sqlite_execution_context import (
    SQLiteExecutionContext,
)
from nre_pipeline.writer.common import DBNLPResultWriter


class SQLiteWriter(DBNLPResultWriter):
    def __init__(self, db_path: str | None = None):
        self.db_path = self._db_path(db_path)
        self.ensure_table(
            """
                CREATE TABLE IF NOT EXISTS nlp_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT,
                    result TEXT
                )
            """
        )

    def _db_path(self, db_path: str | None) -> str:
        _path = db_path or os.getenv("RESULTS_PATH", None)
        if _path is None:
            raise ValueError(
                "Database path must be provided either as an argument or via the RESULTS_PATH environment variable."
            )
        return cast(str, _path)

    def _record(self, nlp_result: NLPResult, context: DatabaseExecutionContext) -> None:
        record: Dict[str, Any] = {
            "document_id": nlp_result.note_id,
        }
        record.update(**nlp_result.results)
        query: str = (
            f"INSERT INTO nlp_results ({', '.join(record.keys())}) VALUES (?, ?)"
        )
        context.insert(query, tuple(record.values()))

    def _get_database_context(self) -> DatabaseExecutionContext:
        return SQLiteExecutionContext(self.db_path)

    def on_transaction_begin(self, context: DatabaseExecutionContext) -> None:
        logger.debug("Transaction started.")

    def on_transaction_commit(self, context: DatabaseExecutionContext) -> None:
        logger.debug("Transaction committed.")

    def on_transaction_rollback(self, context: DatabaseExecutionContext) -> None:
        logger.debug("Transaction rolled back.")
