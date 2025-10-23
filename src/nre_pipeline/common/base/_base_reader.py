import os
import queue
from abc import abstractmethod
from typing import Any, Iterator, Optional, Self
from nre_pipeline.app.verbose_mixin import VerboseMixin
from ._base_process import _BaseProcess
from nre_pipeline.common.base._consts import QUEUE_EMPTY, TProcessingStatus, TQueueEmpty
from nre_pipeline.models import Document
from nre_pipeline.models._batch import DocumentBatch
from loguru import logger


class CorpusReader(_BaseProcess, VerboseMixin):
    """
    Abstract base class for corpus readers that iterate over files.
    """

    def __init__(
        self,
        inqueue: queue.Queue[DocumentBatch | TQueueEmpty],
        total_read,
        doc_batch_size: int | None = None,
        **config,
    ) -> None:

        self._init_debug_config(config)
        super().__init__()
        self._doc_batch_size: int = self._get_document_batch_size(doc_batch_size)
        self._total_documents_read = total_read
        self._inqueue: queue.Queue[DocumentBatch | TQueueEmpty] = inqueue

        #########################################################################
        # Reader tracking
        #########################################################################
        self._reader_status: TProcessingStatus = "not_started"

    @classmethod
    def create(cls, manager, **config) -> Self:
        inqueue_size = int(os.getenv("INQUEUE_MAX_DOCBATCH_COUNT", -1))
        if inqueue_size < 1:
            raise ValueError("INQUEUE_MAX_DOCBATCH_COUNT must be at least 1")
        inqueue: queue.Queue[DocumentBatch | TQueueEmpty] = manager.Queue(inqueue_size)
        total_read = manager.Value("i", 0)
        config["inqueue"] = inqueue
        config["total_read"] = total_read
        return cls(**config)

    def _runner(self) -> None:
        """Run the reader process."""
        try:
            for document_batch in self._iter():
                self._reader_status = "processing"

                self._debug_log("Starting reader loop")
                # Iterate through all batches

                self._place_document_batch_in_queue(document_batch)

            self._mark_all_documents_read()
            self._reader_status = "complete"
        except Exception as e:
            logger.error(f"Error occurred in reader loop: {e}")
            self._reader_status = "failure"
        finally:
            self._debug_log("Reader loop finished")

    @property
    def total_documents_read(self):
        """Get the total number of documents read.

        Returns:
            int: The total number of documents read.
        """
        return self._total_documents_read

    @property
    def inqueue(self) -> queue.Queue[DocumentBatch | TQueueEmpty]:
        return self._inqueue

    @abstractmethod
    def _iter(self) -> Iterator[DocumentBatch]:
        """
        Return an iterator that yields files.

        Yields:
            Path: Each file found
        """
        pass

    def _get_document_batch_size(self, doc_batch_size: int | None = None) -> int:
        """Get the document batch size.

        Args:
            doc_batch_size (int | None, optional): The desired document batch size. Defaults to None.

        Raises:
            ValueError: If the document batch size is invalid.

        Returns:
            int: The effective document batch size.
        """
        document_batch_size: int = doc_batch_size or int(
            os.getenv("DOCUMENT_BATCH_SIZE", -1)
        )
        if document_batch_size < 1:
            raise ValueError(
                "Batch size must be at least 1 or DOCUMENT_BATCH_SIZE must be defined"
            )

        return document_batch_size

    def _mark_all_documents_read(self) -> None:
        """Mark all documents as read by placing a QUEUE_EMPTY signal in the queue."""
        self._inqueue.put(QUEUE_EMPTY)

    def _place_document_batch_in_queue(self, document_batch) -> None:
        """Place a document batch in the input queue.

        Args:
            document_batch (DocumentBatch): The document batch to place in the queue.
        """
        self._inqueue.put(document_batch)
        new_total = len(document_batch) + self._total_documents_read.get()
        self._total_documents_read.value = new_total

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

    def _init_debug_config(self, config) -> None:
        """Initialize the debug configuration.

        Args:
            config (dict): The configuration dictionary.

        Raises:
            ValueError: If the configuration is invalid.
        """
        self._debug_config = config.pop("debug_config", {})
        self._max_notes_to_read: Optional[int] = config.pop("max_notes_to_read", None)
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


#############################################################
# Limited run code for later
#############################################################

# if self._is_limited_run(doc_count, num_documents_in_batch):
#     # Only send the remaining docs needed to reach max_notes_to_read
#     assert self._max_notes_to_read is not None
#     remaining = self._max_notes_to_read - doc_count
#     if remaining > 0:
#     limited_batch = DocumentBatch(
#         cast(List[Document], document_batch[:remaining])
#     )
#     self._document_batch_inqueue.put(limited_batch)
#     logger.warning(
#     f"Reached max notes to read: {self._max_notes_to_read}"
#     )
#     break

# def _get_max_notes_to_process():
#     debug_max_notes_to_process = os.getenv("DEBUG_MAX_NOTES_TO_PROCESS", None)
#     if debug_max_notes_to_process is None:
#         return None
#     return int(debug_max_notes_to_process)

# def _is_limited_run(self, doc_count, num_documents_in_batch):
#     return (
#         self._max_notes_to_read is not None
#         and doc_count + num_documents_in_batch > self._max_notes_to_read
#     )

#############################################################
# Not currently in use
#############################################################

# def _initialize_read_debug_config():
#     debug_config = {"max_notes_to_read": _get_max_notes_to_process()}
#     logger.debug("max_notes_to_read: {}", debug_config["max_notes_to_read"])
#     return debug_config


# def _get_reader_max_doc_per_batch():
#     reader_max_doc_per_batch = int(os.getenv("READER_MAX_DOC_PER_BATCH", 10))
#     logger.debug("READER_MAX_DOC_PER_BATCH: {}", reader_max_doc_per_batch)
#     return reader_max_doc_per_batch

#############################################################
# If there were ever more than one reader process
#############################################################
# self._num_processor_workers = config.get("num_processor_workers", 1)


#############################################################
# If needed to resize batches
#############################################################
# self._allow_batch_resize = allow_batch_resize

# def resize_batch(self) -> None:
#     """
#     Resize the batch size if allowed.
#     """
#     if self._allow_batch_resize:
#         new_batch_size = self._batch_resize(self._num_processor_workers)
#         if (
#             new_batch_size is not None
#             and new_batch_size != self._doc_batch_size
#             and new_batch_size > MIN_BATCH_SIZE
#         ):
#             self._doc_batch_size = new_batch_size

# # Resize batch to match corpus size, if allowed
# self.resize_batch()


# min_batch_size = os.getenv("MIN_BATCH_SIZE")
# if min_batch_size is None or len(min_batch_size) == 0:
#     MIN_BATCH_SIZE = 100
# else:
#     MIN_BATCH_SIZE = int(min_batch_size)

# @abstractmethod
# def _batch_resize(self, num_processor_workers: int) -> int | None:
#     """
#     Resize the batch size.
#     """
#     raise NotImplementedError("Subclasses must implement this _batch_resize.")

# @staticmethod
# @abstractmethod
# def create_reader(**kwargs) -> Callable[[], "CorpusReader"]:
#     raise NotImplementedError("Subclasses must implement this create_reader.")


#############################################################
# Later for direct iteration
#############################################################
# def __iter__(self) -> Generator[DocumentBatch, Any, None]:
#     """Return an iterator over the document batches.

#     Raises:
#         RuntimeError: If the inqueue is set.

#     Yields:
#         Generator[DocumentBatch, Any, None]: DocumentBatch generator
#     """
#     if self._inqueue is not None:
#         raise RuntimeError("The inqueue is set, so no direct iteration is allowed.")

#     yield from self._iter()
