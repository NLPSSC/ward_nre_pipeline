from multiprocessing import Process
import queue
import threading
from abc import ABC, abstractmethod
from time import sleep
from typing import Any, Generator, cast

from loguru import logger


from nre_pipeline.app.interruptible_mixin import InterruptibleMixin
from nre_pipeline.models._nlp_result import NLPResultFeatures
from nre_pipeline.models._batch import DocumentBatch

from nre_pipeline.processor._not_available_ex import ProcessorNotAvailable
from nre_pipeline.processor.consts import TQueueEmpty, TQueueItem
import queue, threading


class ProcessorQueue:
    """
    ProcessorQueue
    ==============

    A helper that provides a safe, interruptible generator interface over a
    thread-safe queue.Queue instance. Designed to be used by processing
    threads that consume NLPResult items produced by other threads or
    processes.

    Behavior
    --------
    - The generator method next_result() yields items of type `NLPResult`
        retrieved from the underlying queue.
    - It will keep yielding items until the supplied `process_interrupt`
        threading.Event is set, or until a sentinel value (ProcessorQueue.QUEUE_EMPTY)
        is encountered in the queue.
    - While waiting for items it calls queue.get(block=True, timeout=1) so it
        periodically checks the interrupt event and can exit promptly.
    - After the main consumption loop ends (due to interrupt or sentinel),
        next_result() attempts to "drain" any remaining items still present in
        the queue, yielding them until the queue becomes empty.
    - Unexpected exceptions during queue operations are logged and cause
        the generator to stop.

    Key attributes
    --------------
    - QUEUE_EMPTY (class attribute)
            A sentinel value used to signal an explicit end-of-stream. When this
            token is pulled from the queue the generator stops producing further
            results. Its value is the string "QUEUE_EMPTY".
    - _queue
            The underlying queue.Queue instance from which items are consumed.
    - _process_interrupt
            A threading.Event used to signal an external request to stop
            processing. When set, next_result() will stop after finishing the
            current iteration and then drain remaining items.

    Usage example
    -------------
    Typical usage pattern by a consumer thread:


            q = queue.Queue()
            interrupt = threading.Event()
            proc_queue = ProcessorQueue(q, interrupt)

            # Producer thread(s) put NLPResult objects into q
            # When production is finished, a sentinel can be enqueued:
            q.put(ProcessorQueue.QUEUE_EMPTY)

            # Consumer uses the generator to process results
            for result in proc_queue.next_result():
                    # process the NLPResult instance
                    handle_result(result)

            # Alternatively, to stop processing from another thread:
            # interrupt.set()

    Notes and constraints
    ---------------------
    - Items yielded are expected to be of type `NLPResult`. The class does not
        validate item contents beyond casting; callers should ensure items in
        the queue are of the expected shape.
    - The draining phase after interruption will still block briefly (timeout=1)
        while waiting for remaining items. This is intentional to avoid busy-waiting.
    - The class logs errors encountered during queue operations; callers should
        monitor logs for troubleshooting.
    """

    QUEUE_EMPTY: TQueueEmpty = "QUEUE_EMPTY"

    def __init__(self, queue: queue.Queue, process_interrupt: threading.Event) -> None:
        self._queue = queue
        self._process_interrupt: threading.Event = process_interrupt

    def next_result(self) -> Generator[NLPResultFeatures, Any, None]:
        while not self._process_interrupt.is_set():
            try:
                item: TQueueItem = cast(
                    TQueueItem, self._queue.get(block=True, timeout=1)
                )
                if item == ProcessorQueue.QUEUE_EMPTY:
                    raise StopIteration()
                yield cast(NLPResultFeatures, item)
            except queue.Empty:
                continue
            except StopIteration:
                break
            except Exception as e:
                logger.error(f"Error getting item from queue: {e}")
                break

        # Drain remaining items if any
        try:
            while True:
                item = cast(TQueueItem, self._queue.get(block=True, timeout=1))
                yield cast(NLPResultFeatures, item)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error draining queue: {e}")


class Processor(ABC, InterruptibleMixin):
    
    def __init__(
        self,
        processor_id: int,
        writer_queue: queue.Queue,
        process_interrupt: threading.Event,
    ) -> None:
        super().__init__(user_interrupt=process_interrupt)
        self._index = processor_id
        self._writer_queue = writer_queue
        self._available_for_processing = True
        self._lock = threading.Lock()

    def __str__(self):
        return f"[{self.__class__.__name__}] [{self._index}]"

    def __repr__(self) -> str:
        availability = "available" if self._available_for_processing else "busy"
        return f"{super().__str__()} ({availability})"

    @property
    def available_for_processing(self) -> bool:
        with self._lock:
            return self._available_for_processing

    def __call__(self, document_batch: DocumentBatch):
        """Process a document and return the result."""
        with self._lock:
            if self._available_for_processing is False:
                raise ProcessorNotAvailable(self)
            self._available_for_processing = False

        def task():
            try:
                threading.current_thread().name = (
                    f"Processing Batch #{document_batch.batch_id}"
                )
                logger.debug(
                    f"Processor {self} is processing batch {document_batch.batch_id}"
                )
                if self.user_interrupted():
                    logger.warning(f"Processor {self} interrupted by user.")
                    return
                for nlp_result in monitor_call(document_batch):
                    self._writer_queue.put(nlp_result)
                self._writer_queue.put(ProcessorQueue.QUEUE_EMPTY)
            except Exception as e:
                logger.error(f"Error in processor task: {e}")
            finally:
                self._available_for_processing = True

        def monitor_call(_document_batch):
            results = []
            processor_iter: Generator[NLPResultFeatures, Any, None] = (
                self._call_processor(_document_batch)
            )
            if processor_iter is None:
                processor_iter = []
            total = sum(1 for _ in processor_iter)
            # Re-run generator since we exhausted it for counting
            processor_iter = self._call_processor(_document_batch)

            for idx, result in enumerate(processor_iter, 1):
                results.append(result)
            return results

        thread = threading.Thread(target=task)
        thread.start()

        return ProcessorQueue(self._writer_queue, self.get_halt_processing_event())

    @abstractmethod
    def _call_processor(
        self, document_batch: DocumentBatch
    ) -> Generator[NLPResultFeatures, Any, None]:
        """Process a document and return the result."""
        raise NotImplementedError("Subclasses must implement this method.")


