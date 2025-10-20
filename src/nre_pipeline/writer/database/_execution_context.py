from abc import abstractmethod
from contextlib import contextmanager
from typing import List, Self


class DatabaseExecutionContext:
    from nre_pipeline.models._nlp_result import NLPResultFeatures
    from nre_pipeline.writer import database

    def __enter__(self) -> Self:
        # Start the database session
        self.start_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # End the database session
        self.end_session()

    @abstractmethod
    def start_session(self):
        # Logic to start a database session
        pass

    @abstractmethod
    def end_session(self):
        # Logic to end a database session
        pass

    @contextmanager
    def start_transaction(self, transaction_callback):
        try:
            self._start_transaction()
            transaction_callback.on_transaction_begin(self)
            yield
            self.commit_transaction()
            transaction_callback.on_transaction_commit(self)
        except Exception:
            self.rollback_transaction()
            transaction_callback.on_transaction_rollback(self)
            raise

    @abstractmethod
    def _start_transaction(self):
        # Logic to start a database transaction
        raise NotImplementedError("Must implement _start_transaction method.")

    @abstractmethod
    def commit_transaction(self):
        # Logic to commit a database transaction
        raise NotImplementedError("Must implement commit_transaction method.")

    @abstractmethod
    def rollback_transaction(self):
        # Logic to rollback a database transaction
        raise NotImplementedError("Must implement rollback_transaction method.")

    @abstractmethod
    def create_table(self, query: str) -> None:
        raise NotImplementedError("Must implement create_table method.")

    @abstractmethod
    def insert(self, query: str, params: tuple = ()) -> int | None:
        raise NotImplementedError("Must implement insert method.")

    @abstractmethod
    def insert_batch(self, query: str, params_list: List[tuple]) -> None:
        raise NotImplementedError("Must implement insert_batch method.")

    @abstractmethod
    def update(self, query: str, params: tuple = ()) -> int | None:
        raise NotImplementedError("Must implement update method.")

    @abstractmethod
    def select(self, query: str, params: tuple = ()) -> List[NLPResultFeatures]:
        raise NotImplementedError("Must implement select method.")
