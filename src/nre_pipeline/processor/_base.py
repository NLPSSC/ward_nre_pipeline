import queue
import threading
from abc import ABC, abstractmethod
from typing import Any, Generator, cast

from loguru import logger


from nre_pipeline.app.interruptible_mixin import InterruptibleMixin
from nre_pipeline.models._nlp_result import NLPResult
from nre_pipeline.models._batch import DocumentBatch

from nre_pipeline.processor._not_available_ex import ProcessorNotAvailable
from nre_pipeline.processor.consts import TQueueEmpty, TQueueItem


class ProcessorQueue:

    QUEUE_EMPTY: TQueueEmpty = "QUEUE_EMPTY"

    def __init__(self, queue: queue.Queue, process_interrupt: threading.Event) -> None:
        self._queue = queue
        self._process_interrupt: threading.Event = process_interrupt

    def next_result(self) -> Generator[TQueueItem, Any, None]:
        while not self._process_interrupt.is_set():
            try:
                item: TQueueItem = cast(
                    TQueueItem, self._queue.get(block=True, timeout=1)
                )
                if item == ProcessorQueue.QUEUE_EMPTY:
                    raise StopIteration()
                yield item
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
                yield item
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error draining queue: {e}")


class Processor(ABC, InterruptibleMixin):
    def __init__(
        self, processor_id: int, queue: queue.Queue, process_interupt: threading.Event
    ) -> None:
        super().__init__(user_interrupt=process_interupt)
        self._index = processor_id
        self._queue = queue
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
                    self._queue.put(nlp_result)
                self._queue.put(ProcessorQueue.QUEUE_EMPTY)
            except Exception as e:
                logger.error(f"Error in processor task: {e}")
            finally:
                self._available_for_processing = True

        def monitor_call(_document_batch):
            results = []
            processor_iter: Generator[NLPResult, Any, None] = self._call_processor(
                _document_batch
            )
            if processor_iter is None:
                processor_iter = []
            total = sum(1 for _ in processor_iter)
            # Re-run generator since we exhausted it for counting
            processor_iter = self._call_processor(_document_batch)
            if processor_iter is None:
                processor_iter = []
            for idx, result in enumerate(processor_iter, 1):
                results.append(result)
            return results

        thread = threading.Thread(target=task)
        thread.start()

        return ProcessorQueue(self._queue, self.get_halt_processing_event())

    @abstractmethod
    def _call_processor(
        self, document_batch: DocumentBatch
    ) -> Generator[NLPResult, Any, None]:
        """Process a document and return the result."""
        raise NotImplementedError("Subclasses must implement this method.")
