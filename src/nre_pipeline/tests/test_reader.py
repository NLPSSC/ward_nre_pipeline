import os
import psutil
from typing import Iterator
from loguru import logger
from nre_pipeline.common import setup_logging
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.reader._filesystem_reader import FileSystemReader


TEST_DATA_PATH = os.getenv("TEST_DATA_PATH")
if not TEST_DATA_PATH:
    raise ValueError("TEST_DATA_PATH environment variable is not set")


def mock_processor(batch) -> int:
    document_count: int = len(batch)
    return document_count


if __name__ == "__main__":
    setup_logging(verbose=False)

    txt_file_count = 0
    for root, dirs, files in os.walk(TEST_DATA_PATH):
        txt_file_count += sum(1 for f in files if f.lower().endswith(".txt"))
    logger.info(f"Total .txt files found: {txt_file_count}")

    reader = FileSystemReader(
        path=TEST_DATA_PATH,
        doc_batch_size=2,
        extensions=[".txt"],
    )

    total_count = 0
    import concurrent.futures

    max_workers = psutil.cpu_count(logical=False) or 4
    logger.info(f"Using {max_workers} worker processes")

    #################################################################################
    # Process batches in parallel using a process pool executor using mock processor
    #################################################################################
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit initial batch of futures
        futures = {}
        reader_iter: Iterator[DocumentBatch] = iter(reader)
        batch_counter = 0

        futures = [executor.submit(mock_processor, doc) for doc in reader_iter]

        for future in concurrent.futures.as_completed(futures):
            total_count += future.result()
        executor.shutdown()

    assert (
        total_count == txt_file_count
    ), f"Expected {txt_file_count} documents, but found {total_count}"

    logger.info(f"Total documents processed: {total_count}")
