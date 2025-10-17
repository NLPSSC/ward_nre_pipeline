import logging
import sys
import threading
from itertools import cycle
from queue import Empty, Queue
from time import sleep
from typing import Any, Callable, Dict, List, Optional, TypeAlias

from nre_pipeline.interruptible_mixin import InterruptibleMixin
from nre_pipeline.processor import Processor
from nre_pipeline.processor._not_available_ex import ProcessorNotAvailable
from nre_pipeline.reader import CorpusReader
from nre_pipeline.writer import NLPResultWriter

logger = logging.getLogger(__name__)


def processor_round_robin(processors: List[Processor]) -> Callable[[int], Processor]:
    """Create a round-robin processor selector."""

    def get_processor(index: int) -> Processor:
        return processors[index % len(processors)]

    return get_processor


PipelineManagerConfig: TypeAlias = Dict[str, Any]


class PipelineManager(InterruptibleMixin):

    

    def __init__(
        self,
        *,
        num_processor_workers: int,
        processor: Callable[[int, Optional[threading.Event]], Processor],
        reader: Callable[[PipelineManagerConfig], CorpusReader],
        writer: Callable[[PipelineManagerConfig], NLPResultWriter],
        queue_size_multiplier: int = 3,
        user_interrupt: Optional[threading.Event] = threading.Event(),
    ) -> None:
        super().__init__(user_interrupt=user_interrupt)
        queue_maxsize = num_processor_workers * queue_size_multiplier
        self._queue: Queue = Queue(maxsize=queue_maxsize)
        self._processors: List[Processor] = [
            processor(i, self._user_interrupt) for i in range(num_processor_workers)
        ]
        for proc in self._processors:
            proc._queue = self._queue  # type: ignore
        config = {"user_interrupt": self._user_interrupt, 'num_processor_workers': num_processor_workers}
        self._processor_iter: cycle = cycle(self._processors)
        self._reader: CorpusReader = reader(config)
        self._writer: NLPResultWriter = writer(config)

        self._processed_batches = 0
        self._start_time = None

    def __enter__(self):
        """Enter the context manager."""
        logger.info("Initializing pipeline resources")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager and cleanup resources."""
        logger.info("Cleaning up pipeline resources")

        # Close reader if it has a cleanup method
        if hasattr(self._reader, "close"):
            try:
                self._reader.close()  # type: ignore
            except Exception as e:
                logger.warning(f"Error closing reader: {e}")

        # Close writer if it has a cleanup method
        if hasattr(self._writer, "close"):
            try:
                self._writer.close()  # type: ignore
            except Exception as e:
                logger.warning(f"Error closing writer: {e}")

        # Log any exception that occurred
        if exc_type is not None:
            logger.error(
                f"Pipeline exited with exception: {exc_type.__name__}: {exc_value}"
            )

        logger.info("Pipeline cleanup completed")

    def run(self) -> None:
        """Run the pipeline."""
        logger.info("Starting pipeline with queue monitoring")

        queue_halt_event = threading.Event()

        # Define Queue Monitor
        def queue_monitor():
            """Monitor the queue and write results."""
            threading.current_thread().name = "Processing Queue Monitor"
            try:
                while not queue_halt_event.is_set():
                    try:
                        item = self._queue.get(timeout=1)
                        if item is not None:
                            self._writer.record(item)
                        self._queue.task_done()
                    except Empty:
                        # Timeout is expected, just continue checking halt event
                        continue
            except Exception as e:
                logger.error(f"Queue monitor encountered error: {e}")
            finally:
                logger.info("Queue monitor shutting down")

        # this thread will be gc'ed when the worker completes
        monitor_thread = threading.Thread(target=queue_monitor, daemon=True)
        monitor_thread.start()

        try:
            for document_batch in self._reader:
                # Wait for an available processor
                while True:
                    try:
                        processor: Processor = next(
                            (x for x in self._processors if x.available_for_processing)
                        )
                        if processor:
                            break
                    except StopIteration:
                        sleep(0.1)

                try:
                    processor(document_batch)
                except ProcessorNotAvailable as e:
                    logger.fatal(
                        f"Processor not available: {e}; logic to wait for availability failed.  Exiting system."
                    )
                    sys.exit(1)

            # Wait for processors to finish
            while any(
                not processor.available_for_processing for processor in self._processors
            ):
                sleep(0.1)
            logger.info("All processors have finished processing")

            # All the processed items should be in queue or written to disk
            self._queue.join()
            logger.info("All results written to disk")

        except Exception as e:
            logger.error(f"Pipeline encountered error: {e}")
        finally:
            # Signal monitor to stop and wait for it
            queue_halt_event.set()
            monitor_thread.join(timeout=10)
            if monitor_thread.is_alive():
                logger.warning("Queue monitor thread did not shut down cleanly")

    def writer_details(self) -> Dict[str, Any]:
        return self._writer.writer_details()
