import os
import queue
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generator, Iterator, List, Optional, cast


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
        if isinstance(self._debug_config, Dict) is False:
            logger.warning(
                "debug_config is not a dictionary; initializing with empty dictionary."
            )
            self._debug_config = {}
        else:
            logger.debug("debug_config set.")
            self._max_notes_to_read = self._debug_config.get("max_notes_to_read", None)
            if isinstance(self._max_notes_to_read, int) is False:
                raise ValueError("max_notes_to_read must be an integer")

    def _reader_loop(self, **kwargs):
        if self._document_batch_inqueue is None:
            raise RuntimeError("The inqueue is not set.")
        assert self._document_batch_inqueue is not None
        self._debug_log("Starting reader loop")
        batch_count = 0
        doc_count = 0
        for batch in self._iter():
            self._debug_log(f"Processing batch {batch_count}")
            if self._document_batch_inqueue is not None:
                # Update the document count
                doc_count += len(batch)

                ##################################################################
                # If self._max_notes_to_read is set, this means we should limit
                # the number of documents read for debugging.
                ##################################################################
                if (
                    self._max_notes_to_read is not None
                    and doc_count >= self._max_notes_to_read
                ):
                    logger.warning(
                        f"Reached max notes to read: {self._max_notes_to_read}"
                    )
                    
                    # If we've reached the max notes to read, we need to adjust the batch size
                    # doc_count - the current count of notes to this point
                    # doc_count % self._max_notes_to_read - the number of notes to read in the last batch

                    # back out the current batch size from the doc count
                    doc_count -= len(batch)
                    # Calculate the number of notes to add in the last batch
                    remaining_notes_to_add = len(batch) - ((doc_count + len(batch)) % self._max_notes_to_read)
                    if remaining_notes_to_add > 0:
                        sub_batch = batch[:remaining_notes_to_add]
                        if isinstance(sub_batch, DocumentBatch):
                            sub_batch = [sub_batch]
                        batch = DocumentBatch(cast(List[Document], sub_batch))
                        self._document_batch_inqueue.put(batch)
                        self._document_batch_inqueue.put(QUEUE_EMPTY)
                    break

                self._document_batch_inqueue.put(batch)
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
