from multiprocessing import Process
import multiprocessing
import os
import queue
import threading
from abc import abstractmethod
from typing import Any, Generator, List, cast
from loguru import logger
from nre_pipeline.app.interruptible_mixin import InterruptibleMixin
from nre_pipeline.app.thread_loop_mixin import ThreadLoopMixin
from nre_pipeline.app.verbose_mixin import VerboseMixin
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.models._batch import DocumentBatch

from nre_pipeline.processor.consts import TQueueEmpty, TQueueItem
import queue, threading


QUEUE_EMPTY: TQueueEmpty = "QUEUE_EMPTY"


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


    def __init__(self, queue: queue.Queue, process_interrupt: threading.Event) -> None:
        self._queue = queue
        self._process_interrupt: threading.Event = process_interrupt

    def next_result(self) -> Generator[NLPResultItem, Any, None]:
        while not self._process_interrupt.is_set():
            try:
                item: TQueueItem = cast(
                    TQueueItem, self._queue.get(block=True, timeout=1)
                )
                if item == QUEUE_EMPTY:
                    raise StopIteration()
                yield cast(NLPResultItem, item)
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
                yield cast(NLPResultItem, item)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error draining queue: {e}")


class Processor(ThreadLoopMixin, InterruptibleMixin, VerboseMixin):

    def __init__(
        self,
        processor_id: int,
        document_batch_inqueue: queue.Queue,
        nlp_results_outqueue: queue.Queue,
        process_interrupt: threading.Event,
        processing_barrier,
        **kwargs,
    ) -> None:
        super().__init__(user_interrupt=process_interrupt, **kwargs)
        self._processor_index = processor_id
        self._document_batch_inqueue = document_batch_inqueue
        self._nlp_results_outqueue = nlp_results_outqueue
        self._processing_barrier = processing_barrier

        # Name the current thread using the derived class name and processor index
        threading.current_thread().name = (
            f"{self.__class__.__name__}-{self._processor_index}"
        )

    def _thread_worker(self):
        self()

    def __repr__(self) -> str:
        return f"[{self.__class__.__name__}] [{self._processor_index}]"

    def __call__(self):
        try:
            # Only the first processor should propagate QUEUE_EMPTY to avoid infinite propagation

            total_output_count = 0
            while not self.user_interrupted():
                try:
                    item = self._document_batch_inqueue.get(block=True, timeout=0.1)
                except queue.Empty:
                    continue
                if item == QUEUE_EMPTY:
                    if self._document_batch_inqueue.qsize() > 0:
                        raise RuntimeError(
                            "Queue is not empty after receiving QUEUE_EMPTY"
                        )
                    self._processing_barrier.wait()
                    logger.debug(
                        "Processing sentinel released for processor {}",
                        self._processor_index,
                    )
                    self._document_batch_inqueue.put(QUEUE_EMPTY)
                    break
                processor_iter: Generator[NLPResultItem, Any, None] = (
                    self._call_processor(cast(DocumentBatch, item))
                )
                for result in processor_iter:
                    total_output_count += 1
                    # logger.debug(
                    #     "Total passed to nlp_results_outqueue: {}", total_output_count
                    # )
                    self._nlp_results_outqueue.put(result)
        except Exception as e:
            logger.error(f"Error in processor loop: {e}")
        finally:
            self.set_complete()
            self.set_user_interrupt()
            

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
