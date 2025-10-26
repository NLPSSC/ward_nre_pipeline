from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Manager, freeze_support
import multiprocessing
import os
import queue
from time import sleep
from typing import cast
from loguru import logger
from nre_pipeline.common import setup_logging
from nre_pipeline.common.base._consts import QUEUE_EMPTY, TQueueEmpty
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.reader._filesystem_reader import FileSystemReader
from tqdm import tqdm
import threading
import time
import atexit


def mock_processor(batch: DocumentBatch) -> int:
    """Mock processor to just get count of docs in batch

    Args:
        batch (DocumentBatch): The batch of documents to process.

    Returns:
        int: The number of documents "processed".
    """
    document_count: int = len(batch)
    return document_count


def get_test_data_path(test_data_path: str | None = None) -> str:
    test_data_path = test_data_path or os.getenv("TEST_DATA_ROOT_PATH")
    if not test_data_path or os.path.exists(test_data_path) is False:
        raise ValueError("TEST_DATA_ROOT_PATH environment variable is not set")
    return test_data_path


def get_total_count_txt_files(test_data_path):
    total_count: int = sum(
        1
        for _, _, files in os.walk(test_data_path)
        for f in files
        if f.lower().endswith(".txt")
    )
    logger.debug(f"Total .txt files found: {total_count}")
    return total_count


if __name__ == "__main__":
    freeze_support()
    setup_logging(verbose=False)

    test_data_path = get_test_data_path()

    txt_file_count: int = get_total_count_txt_files(test_data_path)

    with Manager() as mgr:

        reader: FileSystemReader = FileSystemReader.create(
            manager=mgr,
            input_paths=test_data_path,
            allowed_extensions=[".txt"],
            excluded_paths=[],
        )
        reader.start()

        inqueue: queue.Queue[DocumentBatch | TQueueEmpty] = reader.inqueue

        total_queued: int = 0
        total_processed: int = 0

        pbar = tqdm(total=txt_file_count, unit="doc", desc="Processed", leave=True)
        _stop_event = threading.Event()

        def _monitor():
            last = 0
            while not _stop_event.is_set():
                current_processed: int = total_processed
                diff = current_processed - last
                if diff > 0:
                    pbar.update(diff)
                    last = current_processed
                time.sleep(0.05)

        _monitor_thread = threading.Thread(target=_monitor, daemon=True)
        _monitor_thread.start()

        def _cleanup():
            _stop_event.set()
            _monitor_thread.join(timeout=1)
            try:
                pbar.close()
            except Exception:
                pass

        atexit.register(_cleanup)

        futures = []
        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            while True:
                try:
                    if inqueue.empty():
                        sleep(0.01)
                        continue
                    item: DocumentBatch | TQueueEmpty = inqueue.get(timeout=1)
                    if item == QUEUE_EMPTY:
                        break
                    futures.append(
                        executor.submit(mock_processor, cast(DocumentBatch, item))
                    )
                    total_queued += len(cast(DocumentBatch, item))
                except queue.Empty:
                    continue

                done_futures = [f for f in futures if f.done()]
                total_processed += sum(f.result() for f in done_futures)
                for df in done_futures:
                    futures.remove(df)

            try:
                for f in as_completed(futures):
                    total_processed += f.result()
            except Exception:
                logger.exception("Error processing batch")

        reader.join()

        assert (
            total_processed == txt_file_count
        ), f"Expected {txt_file_count} documents, but found {total_processed}"

        assert (
            reader.total_documents_read.get() == txt_file_count
        ), "Total documents read does not match expected count."

        logger.info(f"Total documents read: {reader.total_documents_read.get()}")
