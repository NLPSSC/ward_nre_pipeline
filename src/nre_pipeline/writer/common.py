from abc import abstractmethod
from multiprocessing import Lock
from typing import List, Union

from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.writer import database
from nre_pipeline.common.base._base_writer import NLPResultWriter


class DBNLPResultWriter(NLPResultWriter, database.TransactionCallbackMixin):
    """Abstract base class for database NLP result writers."""

    _table_create_lock = Lock()

    def __init__(self, *args, **kwargs) -> None:
        self._table_created = False
        super().__init__(*args, **kwargs)

    @property
    def table_name(self) -> str:
        return "nlp_results"

    @abstractmethod
    def get_create_table_query(self, nlp_result: NLPResultItem) -> str:
        """
        Return the SQL query to create the results table for the given NLP result item.
        """
        raise NotImplementedError()

    @abstractmethod
    def _record(self, nlp_result: Union[NLPResultItem, List[NLPResultItem]]) -> None:
        """
        Record one or more NLP result items in the database.
        """
        raise NotImplementedError()

    def record(self, nlp_result: Union[NLPResultItem, List[NLPResultItem]]) -> None:
        """
        Record one or more NLP result items in the database.
        """
        if isinstance(nlp_result, list):
            return self.record_batch(nlp_result)
        self._ensure_table(nlp_result)
        with self._get_database_context() as context:
            with context.start_transaction(self):
                self._record(nlp_result)

    def record_batch(self, nlp_results: List[NLPResultItem]) -> None:
        """
        Batch record multiple NLP results for better performance.
        """
        if not nlp_results:
            return
        self._ensure_table(nlp_results[0])
        self._record_batch(nlp_results)

    def _ensure_table(self, nlp_result: NLPResultItem) -> None:
        """
        Ensure the results table exists in the database.
        """
        with self._table_create_lock:
            if self._table_created is True:
                return
            with self._get_database_context() as context:
                context.create_table(self.get_create_table_query(nlp_result))
            self._table_created = True

    @abstractmethod
    def _get_database_context(self) -> database.DatabaseExecutionContext:
        """
        Get the database execution context.
        """
        raise NotImplementedError()

    @abstractmethod
    def _record_batch(self, nlp_results: List[NLPResultItem]) -> None:
        """
        Record a batch of NLP result items in the database.
        """
        raise NotImplementedError()

    @abstractmethod
    def on_transaction_begin(self, context: database.DatabaseExecutionContext) -> None:
        """
        Begin a database transaction.
        """
        raise NotImplementedError()

    @abstractmethod
    def on_transaction_commit(self, context: database.DatabaseExecutionContext) -> None:
        """
        Commit the current database transaction.
        """
        raise NotImplementedError()

    @abstractmethod
    def on_transaction_rollback(
        self, context: database.DatabaseExecutionContext
    ) -> None:
        """
        Rollback the current database transaction.
        """
        raise NotImplementedError()
