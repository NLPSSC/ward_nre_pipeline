from abc import abstractmethod

from nre_pipeline.models import NLPResult
from nre_pipeline.writer import NLPResultWriter
from nre_pipeline.writer.database import DatabaseExecutionContext
from nre_pipeline.writer.database import TransactionCallbackMixin


class DBNLPResultWriter(NLPResultWriter, TransactionCallbackMixin):
    def record(self, nlp_result: NLPResult) -> None:
        # Get database execution context
        with self._get_database_context() as context:
            with context.start_transaction(self):
                # Perform the actual record operation
                self._record(nlp_result, context)

    def ensure_table(self, table_defn_query: str):
        with self._get_database_context() as context:
            context.create_table(table_defn_query)

    @abstractmethod
    def _get_database_context(self) -> DatabaseExecutionContext:
        """Get the database execution context."""
        raise NotImplementedError()

    @abstractmethod
    def _record(self, nlp_result: NLPResult, context: DatabaseExecutionContext) -> None:
        raise NotImplementedError()

    @abstractmethod
    def on_transaction_begin(self, context: DatabaseExecutionContext) -> None:
        """Begin a database transaction."""
        raise NotImplementedError()

    @abstractmethod
    def on_transaction_commit(self, context: DatabaseExecutionContext) -> None:
        """Commit the current database transaction."""
        raise NotImplementedError()

    @abstractmethod
    def on_transaction_rollback(self, context: DatabaseExecutionContext) -> None:
        """Rollback the current database transaction."""
        raise NotImplementedError()
