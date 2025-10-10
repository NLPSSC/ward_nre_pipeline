import logging
import threading
from itertools import cycle
from queue import Empty, Queue
from typing import Any, Callable, Dict, List

from nre_pipeline.processor import Processor
from nre_pipeline.reader import CorpusReader
from nre_pipeline.writer import NLPResultWriter

logger = logging.getLogger(__name__)


def processor_round_robin(processors: List[Processor]) -> Callable[[int], Processor]:
    """Create a round-robin processor selector."""

    def get_processor(index: int) -> Processor:
        return processors[index % len(processors)]

    return get_processor


class PipelineManager:
    def __init__(
        self,
        *,
        num_processor_workers: int,
        processor: Callable[[int], Processor],
        reader: Callable[[], CorpusReader],
        writer: Callable[[], NLPResultWriter],
    ) -> None:
        self._queue: Queue = Queue(maxsize=num_processor_workers)
        self._processors: List[Processor] = [
            processor(i) for i in range(num_processor_workers)
        ]
        # Set the queue for each processor after creation
        for proc in self._processors:
            proc._queue = self._queue
        self._processor_iter: cycle = cycle(self._processors)
        self._reader: CorpusReader = reader()
        self._writer: NLPResultWriter = writer()

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

        def queue_monitor():
            """Monitor the queue and write results."""
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

        monitor_thread = threading.Thread(target=queue_monitor, daemon=True)
        monitor_thread.start()

        try:
            for document_batch in self._reader:
                processor: Processor = next(self._processor_iter)
                processor(document_batch)

            # Wait for all queued items to be processed
            self._queue.join()
            logger.info("All processing completed")
        finally:
            # Signal monitor to stop and wait for it
            queue_halt_event.set()
            monitor_thread.join(timeout=10)
            if monitor_thread.is_alive():
                logger.warning("Queue monitor thread did not shut down cleanly")

    def writer_details(self) -> Dict[str, Any]:
        return self._writer.writer_details()
