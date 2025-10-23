import os
from pathlib import Path
import sqlite3
from typing import Iterator, List, Union
from regex import D
from nre_pipeline.models._document import Document
from loguru import logger


class DocumentBatch:

    # _db_path = os.getenv("BATCH_ID_PATH", None)

    def __init__(self, documents: List[Document]):
        self._documents: List[Document] = documents
    #     self._batch_id: int = self._get_next_id()
    #     is_inmem: bool = self._db_path is None
    #     if is_inmem:
    #         # use an in-memory SQLite database
    #         raise RuntimeError("In-memory batch ID generation not implemented")
    #         self._db_path = ":memory:"
    #         logger.info("Using in-memory SQLite database for batch IDs")
    #     else:
    #         assert self._db_path is not None
    #         # ensure directory for on-disk DB exists
    #         db_file = Path(self._db_path)
    #         db_file.parent.mkdir(parents=True, exist_ok=True)
    #         logger.info(
    #             f"Using on-disk SQLite database for batch IDs at {self._db_path}"
    #         )

    # @property
    # def batch_id(self) -> int:
    #     return self._batch_id

    # def _get_next_id(self) -> int:

    #     assert self._db_path is not None
    #     conn: sqlite3.Connection = sqlite3.connect(self._db_path)
    #     conn.execute(
    #         "CREATE TABLE IF NOT EXISTS batch_counter (id INTEGER PRIMARY KEY)"
    #     )
    #     cursor = conn.execute("INSERT INTO batch_counter DEFAULT VALUES")
    #     batch_id = cursor.lastrowid
    #     if batch_id is None:
    #         raise RuntimeError("Failed to get next batch ID")
    #     conn.commit()
    #     conn.close()
    #     return batch_id

    def __iter__(self) -> Iterator[Document]:
        return iter(self._documents)

    def __len__(self) -> int:
        return len(self._documents)

    def __getitem__(self, index: int | slice) -> Union[Document, List[Document]]:
        if isinstance(index, slice):
            return self._documents[index]
        if isinstance(index, int):
            return self._documents[index]
        raise TypeError("Index must be an int or a slice")

    def __repr__(self) -> str:
        # return f"DocumentBatch(batch_id={self._batch_id}, doc_count={len(self._documents)})"
        return f"DocumentBatch(doc_count={len(self._documents)})"


class DocumentBatchBuilder:

    def __init__(self, batch_size: int) -> None:
        self._batch_size: int = batch_size
        self._documents: List[Document] = []

    def add_document(self, document: Document) -> Union[DocumentBatch, None]:
        self._documents.append(document)
        if len(self._documents) >= self._batch_size:
            batch = DocumentBatch(self._documents)
            self._documents = []
            return batch
        return None

    def has_docs(self) -> bool:
        return len(self._documents) > 0

    def build(self):
        return DocumentBatch(self._documents)
