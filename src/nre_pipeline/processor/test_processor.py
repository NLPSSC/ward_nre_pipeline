import atexit
from multiprocessing import Manager, freeze_support
import os
import queue
import threading
import time
from typing import List
from loguru import logger
from tqdm import tqdm
from nre_pipeline.common import setup_logging
from nre_pipeline.common.base._consts import TQueueEmpty
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.processor.noop_processor import NoOpProcessor
from nre_pipeline.reader._filesystem_reader import FileSystemReader


def get_test_data_path(test_data_path: str | None = None) -> str:
    test_data_path = test_data_path or os.getenv("TEST_DATA_PATH")
    if not test_data_path or os.path.exists(test_data_path) is False:
        raise ValueError("TEST_DATA_PATH environment variable is not set")
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

    test_data_path = get_test_data_path("/input_data/Am_J_Dent_Sci/1839")

    txt_file_count: int = get_total_count_txt_files(test_data_path)

    with Manager() as mgr:

        reader: FileSystemReader = FileSystemReader.create(
            manager=mgr,
            input_paths=test_data_path,
            allowed_extensions=[".txt"],
            excluded_paths=[],
        )
        reader.start()

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

        inqueue: queue.Queue[DocumentBatch | TQueueEmpty] = reader.inqueue
        processors: List[NoOpProcessor]
        outqueue: queue.Queue[NLPResultItem | TQueueEmpty]
        processors, outqueue = NoOpProcessor.create(
            mgr, **{"num_workers": 1, "inqueue": inqueue}
        )
        for p in processors:
            p.start()

        while True:
            try:
                item: NLPResultItem | TQueueEmpty = outqueue.get(timeout=1)
                if item == "QUEUE_EMPTY":
                    break
                total_processed += 1
            except queue.Empty:
                if not any(p.is_alive() for p in processors):
                    break
                continue

        reader.join()
        total_docs_processed = processors[0].total_docs_processed
        for p in processors:
            p.join()

        logger.debug("Total docs processed: {}", total_docs_processed.get())
        logger.complete()
