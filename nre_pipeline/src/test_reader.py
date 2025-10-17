import os
from concurrent.futures import Future
from typing import Any, Generator

from loguru import logger

from nre_pipeline import setup_logging
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.reader._filesystem import FileSystemReader
import psutil


def process_batch(batch):
    document_count: int = len(batch)
    return document_count


if __name__ == "__main__":
    setup_logging(False)

    txt_file_count = 0
    test_case_path = (
        r"Z:\_\data\corpora\ocred_docs_from_pubmed\Buffalo_Med_J_Mon_Rev_Med_Surg_Sci"
    )
    for root, dirs, files in os.walk(test_case_path):
        txt_file_count += sum(1 for f in files if f.lower().endswith(".txt"))
    logger.info(f"Total .txt files found: {txt_file_count}")

    reader = FileSystemReader(
        path=test_case_path,
        batch_size=1000,
        extensions=[".txt"],
    )

    total_count = 0
    import concurrent.futures

    max_workers = psutil.cpu_count(logical=False) or 4
    logger.info(f"Using {max_workers} worker processes")
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit initial batch of futures
        futures = {}
        reader_iter: Generator[DocumentBatch, Any, None] = iter(reader)
        batch_counter = 0

        # Fill the initial queue
        for _ in range(max_workers * 2):  # Keep 2x workers busy
            try:
                batch: DocumentBatch = next(reader_iter)
                future: Future[int] = executor.submit(process_batch, batch)
                futures[future] = batch_counter
                batch_counter += 1
            except StopIteration:
                break

        # Process futures as they complete and submit new ones
        while futures:  # Continue until all futures are done
            for future in concurrent.futures.as_completed(futures):
                result: int = future.result()
                batch_idx = futures[future]
                total_count += result
                logger.debug(f"Batch {batch_idx}: {result}")

                # Submit next batch if available
                try:
                    batch = next(reader_iter)
                    new_future = executor.submit(process_batch, batch)
                    futures[new_future] = batch_counter
                    batch_counter += 1
                except StopIteration:
                    pass

                # Clean up completed future
                del futures[future]
                break  # Break to restart as_completed with updated futures dict

    assert total_count == txt_file_count, (
        f"Expected {txt_file_count} documents, but found {total_count}"
    )

    logger.info(f"Total documents processed: {total_count}")
