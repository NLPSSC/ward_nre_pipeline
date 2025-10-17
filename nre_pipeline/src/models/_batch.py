import os
from pathlib import Path
import sqlite3
from typing import Iterator, List

from nre_pipeline.models._document import Document


class DocumentBatch:
    
    batch_id_path = os.getenv("BATCH_ID_PATH", None)
    if batch_id_path is None:
        raise ValueError("BATCH_ID_PATH environment variable is not set")
    
    _db_path = Path(batch_id_path)

    def __init__(self, documents: List[Document]):
        self._documents: List[Document] = documents
        self._batch_id: int = self._get_next_id()

    @property
    def batch_id(self) -> int:
        return self._batch_id

    def _get_next_id(self) -> int:
        conn: sqlite3.Connection = sqlite3.connect(self._db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS batch_counter (id INTEGER PRIMARY KEY)"
        )
        cursor = conn.execute("INSERT INTO batch_counter DEFAULT VALUES")
        batch_id = cursor.lastrowid
        if batch_id is None:
            raise RuntimeError("Failed to get next batch ID")
        conn.commit()
        conn.close()
        return batch_id

    def __iter__(self) -> Iterator[Document]:
        return iter(self._documents)

    def __len__(self) -> int:
        return len(self._documents)

    def __getitem__(self, index: int) -> Document:
        return self._documents[index]
