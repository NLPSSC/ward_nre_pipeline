import sqlite3
from pathlib import Path
from typing import List

from nre_pipeline.models import NLPResult
from nre_pipeline.writer.database import DatabaseExecutionContext


class SQLiteExecutionContext(DatabaseExecutionContext):
    def __init__(self, db_path: str):
        self._db_path = Path(db_path)

    def __enter__(self):
        # Ensure the parent directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection = sqlite3.connect(str(self._db_path))

        # Optimize SQLite for performance
        self._conn.execute(
            "PRAGMA journal_mode=WAL"
        )  # Write-Ahead Logging for better concurrency
        self._conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
        self._conn.execute("PRAGMA cache_size=10000")  # Larger cache
        self._conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
        self._conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O

        self._cursor: sqlite3.Cursor = self._conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit_transaction()
        self._conn.close()

    def _start_transaction(self):
        # Logic to start a database transaction
        self._conn.execute("BEGIN")

    def commit_transaction(self):
        # Logic to commit a database transaction
        self._conn.commit()

    def rollback_transaction(self):
        # Logic to rollback a database transaction
        self._conn.rollback()

    def create_table(self, query: str) -> None:
        self._cursor.execute(query)
        self._conn.commit()

    def insert(self, query: str, params: tuple = ()) -> int | None:
        self._cursor.execute(query, params)
        return self._cursor.lastrowid

    def insert_batch(self, query: str, params_list: List[tuple]) -> None:
        """Execute batch insert for better performance."""
        self._cursor.executemany(query, params_list)

    def update(self, query: str, params: tuple = ()) -> int | None:
        self._cursor.execute(query, params)
        return self._cursor.rowcount

    def select(self, query: str, params: tuple = ()) -> List[NLPResult]:
        self._cursor.execute(query, params)
        rows = self._cursor.fetchall()
        return [NLPResult(**row) for row in rows]
