import os
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterator

from nre_pipeline.interruptible_mixin import InterruptibleMixin
from nre_pipeline.models import Document
from nre_pipeline.models._batch import DocumentBatch

MIN_BATCH_SIZE = int(os.getenv("MIN_BATCH_SIZE", 100))


class CorpusReader(ABC, InterruptibleMixin):
    """
    Abstract base class for corpus readers that iterate over files.
    """

    def __init__(
        self,
        batch_size: int,
        allow_batch_resize: bool = False,
        user_interrupt: threading.Event | None = None,
        **config
    ) -> None:
        super().__init__(user_interrupt=user_interrupt)
        self._num_processor_workers = config.get("num_processor_workers", 1)
        self._allow_batch_resize = allow_batch_resize
        self._batch_size = batch_size

    def resize_batch(self):
        """
        Resize the batch size if allowed.
        """
        if self._allow_batch_resize:
            new_batch_size = self._batch_resize(self._num_processor_workers)
            if (
                new_batch_size is not None
                and new_batch_size != self._batch_size
                and new_batch_size > MIN_BATCH_SIZE
            ):
                self._batch_size = new_batch_size

    @abstractmethod
    def _batch_resize(self, num_processor_workers: int) -> int | None:
        """
        Resize the batch size.
        """
        raise NotImplementedError("Subclasses must implement this _batch_resize.")

    @staticmethod
    @abstractmethod
    def create_reader(**kwargs) -> Callable[[], "CorpusReader"]:
        raise NotImplementedError("Subclasses must implement this create_reader.")

    def __iter__(self) -> Iterator[DocumentBatch]:
        # Resize batch to match corpus size, if allowed
        self.resize_batch()

        for batch in self._iter():
            if self.user_interrupted():
                break
            yield batch

    @abstractmethod
    def _iter(self) -> Iterator[DocumentBatch]:
        """
        Return an iterator that yields files.

        Yields:
            Path: Each file found
        """
        pass

    @abstractmethod
    def make_doc(self, source: Any) -> Document:
        """
        Create a Document object from the given source.

        Args:
            source: The source from which to create the Document

        Returns:
            Document: The created Document object
        """
        raise NotImplementedError()
