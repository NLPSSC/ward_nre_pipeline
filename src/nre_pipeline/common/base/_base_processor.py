from multiprocessing import Process
import multiprocessing
import os
import queue
import threading
from abc import abstractmethod
from typing import Any, Dict, Generator, List, Self, Tuple, cast
from loguru import logger
from nre_pipeline.app.verbose_mixin import VerboseMixin
from nre_pipeline.common.base._component_base import _BaseProcess
from nre_pipeline.common.base._consts import (
    PROCESSING_COMPLETED,
    QUEUE_EMPTY,
    TQueueEmpty,
)
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.models._batch import DocumentBatch

import queue, threading


# class ProcessorQueue:
#     """
#     ProcessorQueue
#     ==============

#     A helper that provides a safe, interruptible generator interface over a
#     thread-safe queue.Queue instance. Designed to be used by processing
#     threads that consume NLPResult items produced by other threads or
#     processes.

#     Behavior
#     --------
#     - The generator method next_result() yields items of type `NLPResult`
#         retrieved from the underlying queue.
#     - It will keep yielding items until the supplied `process_interrupt`
#         threading.Event is set, or until a sentinel value (QUEUE_EMPTY)
#         is encountered in the queue.
#     - While waiting for items it calls queue.get(block=True, timeout=1) so it
#         periodically checks the interrupt event and can exit promptly.
#     - After the main consumption loop ends (due to interrupt or sentinel),
#         next_result() attempts to "drain" any remaining items still present in
#         the queue, yielding them until the queue becomes empty.
#     - Unexpected exceptions during queue operations are logged and cause
#         the generator to stop.

#     Key attributes
#     --------------
#     - QUEUE_EMPTY (class attribute)
#             A sentinel value used to signal an explicit end-of-stream. When this
#             token is pulled from the queue the generator stops producing further
#             results. Its value is the string "QUEUE_EMPTY".
#     - _queue
#             The underlying queue.Queue instance from which items are consumed.
#     - _process_interrupt
#             A threading.Event used to signal an external request to stop
#             processing. When set, next_result() will stop after finishing the
#             current iteration and then drain remaining items.

#     Usage example
#     -------------
#     Typical usage pattern by a consumer thread:


#             q = queue.Queue()
#             interrupt = threading.Event()
#             proc_queue = ProcessorQueue(q, interrupt)

#             # Producer thread(s) put NLPResult objects into q
#             # When production is finished, a sentinel can be enqueued:
#             q.put(QUEUE_EMPTY)

#             # Consumer uses the generator to process results
#             for result in proc_queue.next_result():
#                     # process the NLPResult instance
#                     handle_result(result)

#             # Alternatively, to stop processing from another thread:
#             # interrupt.set()

#     Notes and constraints
#     ---------------------
#     - Items yielded are expected to be of type `NLPResult`. The class does not
#         validate item contents beyond casting; callers should ensure items in
#         the queue are of the expected shape.
#     - The draining phase after interruption will still block briefly (timeout=1)
#         while waiting for remaining items. This is intentional to avoid busy-waiting.
#     - The class logs errors encountered during queue operations; callers should
#         monitor logs for troubleshooting.
#     """

#     def __init__(self, queue: queue.Queue, process_interrupt: threading.Event) -> None:
#         self._queue = queue
#         self._process_interrupt: threading.Event = process_interrupt

#     def next_result(self) -> Generator[NLPResultItem, Any, None]:
#         while not self._process_interrupt.is_set():
#             try:
#                 item: TQueueItem = cast(
#                     TQueueItem, self._queue.get(block=True, timeout=1)
#                 )
#                 if item == QUEUE_EMPTY:
#                     raise StopIteration()
#                 yield cast(NLPResultItem, item)
#             except queue.Empty:
#                 continue
#             except StopIteration:
#                 break
#             except Exception as e:
#                 logger.error(f"Error getting item from queue: {e}")
#                 break

#         # Drain remaining items if any
#         try:
#             while True:
#                 item = cast(TQueueItem, self._queue.get(block=True, timeout=1))
#                 yield cast(NLPResultItem, item)
#         except queue.Empty:
#             pass
#         except Exception as e:
#             logger.error(f"Error draining queue: {e}")


class Processor(_BaseProcess, VerboseMixin):

    def __init__(
        self,
        processor_id: int,
        total_documents_processed,
        inqueue: queue.Queue[DocumentBatch | TQueueEmpty],
        outqueue: queue.Queue[NLPResultItem | TQueueEmpty],
        process_counter,
        processor_lock,
        inqueue_empty_sentinel,
        **config,
    ) -> None:
        self._process_name = f"{self.__class__.__name__}-{processor_id}"
        self._processor_config = cast(
            Dict[str, Any], config.pop("processor_config", {})
        )
        super().__init__(**config)
        self._process_counter = process_counter
        self._processor_index: int = processor_id
        self._inqueue: queue.Queue[DocumentBatch | TQueueEmpty] = inqueue
        self._outqueue: queue.Queue[NLPResultItem | TQueueEmpty] = outqueue
        self._total_documents_processed = total_documents_processed
        self._processor_lock = processor_lock
        self._inqueue_empty_sentinel = inqueue_empty_sentinel

        # Name the current thread using the derived class name and processor index
        threading.current_thread().name = (
            f"{self.__class__.__name__}-{self._processor_index}"
        )

    @property
    def processor_config(self) -> Dict[str, Any]:
        return self._processor_config

    @classmethod
    def create(
        cls, manager, **config
    ) -> Tuple[List[Self], queue.Queue[NLPResultItem | TQueueEmpty], Any]:

        num_workers: int = int(config.pop("num_workers", -1))
        if num_workers < 1:
            raise ValueError("num_workers must be a positive integer")

        inqueue = config.get("inqueue")
        if inqueue is None:
            raise RuntimeError("inqueue must be provided")

        process_counter = manager.Value("i", num_workers)
        processor_lock = manager.Lock()
        inqueue_empty_sentinel = manager.Event()

        ###############################################################################
        # One outqueue to rule them all...
        ###############################################################################
        outqueue_size = int(os.getenv("OUTQUEUE_MAX_DOCBATCH_COUNT", -1))
        if outqueue_size < 1:
            raise ValueError("OUTQUEUE_MAX_DOCBATCH_COUNT must be a positive integer")

        outqueue: queue.Queue[NLPResultItem | TQueueEmpty] = manager.Queue(
            outqueue_size
        )

        total_documents_processed = manager.Value("i", 0)
        processor_ids: List[int] = list(range(num_workers))

        configs = []
        for proc_id in processor_ids:
            new_config = {k: v for k, v in config.items()}
            new_config["inqueue"] = inqueue
            new_config["outqueue"] = outqueue
            new_config["total_documents_processed"] = total_documents_processed
            new_config["processor_id"] = proc_id
            new_config["process_counter"] = process_counter
            new_config["processor_lock"] = processor_lock
            new_config["inqueue_empty_sentinel"] = inqueue_empty_sentinel
            configs.append(new_config)

        processors = []
        for config in configs:
            processors.append(cls(**config))

        return processors, outqueue, process_counter

    def _runner(self):
        try:
            # Only the first processor should propagate QUEUE_EMPTY to avoid infinite propagation

            while not self._inqueue_empty_sentinel.is_set():
                try:
                    item = self._inqueue.get(block=True, timeout=5)
                except queue.Empty:
                    # logger.debug(
                    #     "Processor {} queue empty, continuing...",
                    #     self.get_process_name(),
                    # )
                    continue

                if isinstance(item, DocumentBatch):
                    doc_batch: DocumentBatch = cast(DocumentBatch, item)
                    total_output_count = self.total_docs_processed.get()
                    for result in self._call_processor(doc_batch):
                        total_output_count += 1
                        self._outqueue.put(result)
                    self.update_total_docs_processed(total_output_count)
                else:
                    #############################################################################
                    # Check for sentinel value indicating no more items
                    # If exists, propagate it, update the process counter, then
                    # exit this processor
                    #############################################################################
                    with self._processor_lock:
                        if item == QUEUE_EMPTY or self._inqueue_empty_sentinel.is_set():
                            logger.debug(
                                "Processor count: {}", self._process_counter.get()
                            )
                            self._inqueue_empty_sentinel.set()

                            break

        except Exception as e:
            logger.error(f"Error in processor loop: {e}")
        finally:
            with self._processor_lock:
                self._outqueue.put(QUEUE_EMPTY)
                if self._process_counter.get() > 0:
                    self._process_counter.set(self._process_counter.get() - 1)

            logger.debug("{} processor exiting...", self.get_process_name())

    def get_process_name(self):
        return self._process_name

    @property
    def total_docs_processed(self):
        return self._total_documents_processed

    def update_total_docs_processed(self, total_count: int):
        with self._processor_lock:
            new_total = self._total_documents_processed.get() + total_count
            self._total_documents_processed.set(new_total)

    def __repr__(self) -> str:
        return f"[{self.__class__.__name__}] [{self._processor_index}]"

    @abstractmethod
    def _call_processor(
        self, document_batch: DocumentBatch
    ) -> Generator[NLPResultItem, Any, None]:
        """Process a document and return the result."""
        raise NotImplementedError("Subclasses must implement this method.")


def _get_num_processors_to_create():
    num_processors_to_create = os.getenv("NUM_PROCESSORS_TO_CREATE", None)
    if num_processors_to_create is None or len(num_processors_to_create) == 0:
        num_processors_to_create = multiprocessing.cpu_count()
    else:
        num_processors_to_create = int(num_processors_to_create)
    logger.debug("NUM_PROCESSORS_TO_CREATE: {}", num_processors_to_create)
    return num_processors_to_create


def initialize_nlp_processes(processor_type, config, manager):

    configs = []

    num_processes_to_create = _get_num_processors_to_create()
    processing_barrier = manager.Barrier(num_processes_to_create)
    for idx in range(num_processes_to_create):
        new_config = {k: v for k, v in config.items()}

        logger.debug(
            "Acquiring semaphore for processor {}",
            idx,
        )
        new_config.update(
            {"processor_id": idx, "processing_barrier": processing_barrier}
        )
        configs.append(new_config)

    nlp_processes: List[Process] = [
        Process(
            target=processor_type,
            kwargs=config,
        )
        for config in configs
    ]

    for p in nlp_processes:
        p.start()

    return nlp_processes, processing_barrier
