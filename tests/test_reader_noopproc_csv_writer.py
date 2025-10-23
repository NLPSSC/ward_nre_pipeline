import atexit
from multiprocessing import Manager, freeze_support
import os
import threading
import time
from loguru import logger
from tqdm import tqdm
from nre_pipeline.common import setup_logging
from nre_pipeline.processor.noop_processor import NoOpProcessor
from nre_pipeline.reader._filesystem_reader import FileSystemReader
from nre_pipeline.writer.filesystem._csv_writer import CSVWriter


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

        total_queued: int = 0
        total_processed: int = 0

        processors, outqueue = NoOpProcessor.create(
            mgr, **{"num_workers": 2, "inqueue": reader.inqueue}
        )
        writer: CSVWriter = CSVWriter.create(mgr, **{"outqueue": outqueue})

        reader.start()
        for p in processors:
            p.start()
        writer.start()

        reader.join()
        total_docs_processed = processors[0].total_docs_processed
        for p in processors:
            p.join()
        writer.join()

        logger.debug("Total docs processed: {}", total_docs_processed.get())
        logger.complete()
