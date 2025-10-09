from abc import abstractmethod
from multiprocessing import Lock

from nre_pipeline.models import NLPResult
from nre_pipeline.writer import NLPResultWriter, database


class DBNLPResultWriter(NLPResultWriter, database.TransactionCallbackMixin):
    """Abstract base class for database NLP result writers."""

    _table_create_lock = Lock()

    def __init__(self) -> None:
        self._table_created = False
        super().__init__()

    @property
    def table_name(self) -> str:
        return "nlp_results"

    @abstractmethod
    def get_create_table_query(self, nlp_result: NLPResult) -> str:
        raise NotImplementedError()

    def record(self, nlp_result: NLPResult) -> None:
        self._ensure_table(nlp_result)
        # Get database execution context
        with self._get_database_context() as context:
            with context.start_transaction(self):
                # Perform the actual record operation
                self._record(nlp_result, context)

    def _ensure_table(self, nlp_result: NLPResult):
        with self._table_create_lock:
            if self._table_created is True:
                return
            with self._get_database_context() as context:
                context.create_table(self.get_create_table_query(nlp_result))
            self._table_created = True

    @abstractmethod
    def _get_database_context(self) -> database.DatabaseExecutionContext:
        """Get the database execution context."""
        raise NotImplementedError()

    @abstractmethod
    def _record(
        self, nlp_result: NLPResult, context: database.DatabaseExecutionContext
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def on_transaction_begin(self, context: database.DatabaseExecutionContext) -> None:
        """Begin a database transaction."""
        raise NotImplementedError()

    @abstractmethod
    def on_transaction_commit(self, context: database.DatabaseExecutionContext) -> None:
        """Commit the current database transaction."""
        raise NotImplementedError()

    @abstractmethod
    def on_transaction_rollback(
        self, context: database.DatabaseExecutionContext
    ) -> None:
        """Rollback the current database transaction."""
        raise NotImplementedError()
