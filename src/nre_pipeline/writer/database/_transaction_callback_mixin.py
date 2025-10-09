from abc import ABC, abstractmethod

from nre_pipeline.writer.database import DatabaseExecutionContext


class TransactionCallbackMixin(ABC):
    @abstractmethod
    def on_transaction_begin(self, context: DatabaseExecutionContext) -> None:
        """Callback invoked at the beginning of a transaction."""
        pass

    @abstractmethod
    def on_transaction_commit(self, context: DatabaseExecutionContext) -> None:
        """Callback invoked upon successful commit of a transaction."""
        pass

    @abstractmethod
    def on_transaction_rollback(self, context: DatabaseExecutionContext) -> None:
        """Callback invoked when a transaction is rolled back."""
        pass
