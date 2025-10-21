import os
import queue
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable, Generator, Iterator, List, Optional, cast


from nre_pipeline.app.interruptible_mixin import InterruptibleMixin
from nre_pipeline.app.thread_loop_mixin import ThreadLoopMixin
from nre_pipeline.app.verbose_mixin import VerboseMixin
from nre_pipeline.models import Document
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.processor._base import QUEUE_EMPTY

from loguru import logger

MIN_BATCH_SIZE = int(os.getenv("MIN_BATCH_SIZE", 100))


class CorpusReader(ABC, InterruptibleMixin, VerboseMixin, ThreadLoopMixin):
    """
    Abstract base class for corpus readers that iterate over files.
    """

    def __init__(
        self,
        doc_batch_size: int,
        user_interrupt: threading.Event,
        allow_batch_resize: bool = False,
        document_batch_inqueue: Optional[queue.Queue] = None,
        **config,
    ) -> None:
        super().__init__(
            user_interrupt=user_interrupt, target=self._reader_loop, **config
        )
        self._num_processor_workers = config.get("num_processor_workers", 1)
        self._allow_batch_resize = allow_batch_resize
        self._doc_batch_size = doc_batch_size
        self._document_batch_inqueue: Optional[queue.Queue] = document_batch_inqueue
        self._debug_config = config.get("debug_config", {})
        self._max_notes_to_read: Optional[int] = None
        self._init_debug_config()

    def _init_debug_config(self) -> None:
        if not isinstance(self._debug_config, dict):
            logger.warning(
                "debug_config is not a dictionary; initializing with empty dictionary."
            )
            self._debug_config = {}
        logger.debug("debug_config set.")
        self._max_notes_to_read = self._debug_config.get("max_notes_to_read", None)
        if self._max_notes_to_read is not None and not isinstance(
            self._max_notes_to_read, int
        ):
            raise ValueError("max_notes_to_read must be an integer")

    def _reader_loop(self, **kwargs):
        if self._document_batch_inqueue is None:
            raise RuntimeError("The inqueue is not set.")
        self._debug_log("Starting reader loop")
        doc_count = 0
        for batch in self._iter():
            batch_len = len(batch)
            if self._max_notes_to_read is not None:
                if doc_count + batch_len > self._max_notes_to_read:
                    # Only send the remaining docs needed to reach max_notes_to_read
                    remaining = self._max_notes_to_read - doc_count
                    if remaining > 0:
                        limited_batch = DocumentBatch(
                            cast(List[Document], batch[:remaining])
                        )
                        self._document_batch_inqueue.put(limited_batch)
                    logger.warning(
                        f"Reached max notes to read: {self._max_notes_to_read}"
                    )
                    break
            self._document_batch_inqueue.put(batch)
            doc_count += batch_len
            if self.user_interrupted():
                self._debug_log("User interrupt detected")
                break
        self._document_batch_inqueue.put(QUEUE_EMPTY)

    def resize_batch(self) -> None:
        """
        Resize the batch size if allowed.
        """
        if self._allow_batch_resize:
            new_batch_size = self._batch_resize(self._num_processor_workers)
            if (
                new_batch_size is not None
                and new_batch_size != self._doc_batch_size
                and new_batch_size > MIN_BATCH_SIZE
            ):
                self._doc_batch_size = new_batch_size

    def __iter__(self) -> Generator[DocumentBatch, Any, None]:

        if self._document_batch_inqueue is not None:
            raise RuntimeError("The inqueue is set, so no direct iteration is allowed.")
        # Resize batch to match corpus size, if allowed
        self.resize_batch()

        for batch in self._iter():
            yield batch
            if self.user_interrupted():
                self._debug_log("User interrupt detected")

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
