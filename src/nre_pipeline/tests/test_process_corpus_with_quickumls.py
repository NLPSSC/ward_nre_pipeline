#!/usr/bin/env python3
"""
Simple test for MedspacyUmlsProcessor to debug the matching issue.
"""

from time import sleep
import psutil

from multiprocessing import Manager, Process, freeze_support
import queue
from typing import cast
from nre_pipeline.common import setup_logging
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.processor._base import ProcessorQueue
from nre_pipeline.processor.quickumls_processor._quickumls import QuickUMLSProcessor
from nre_pipeline.reader._filesystem import FileSystemReader
from nre_pipeline.writer.database._sqlite import SQLiteNLPWriter

logger = setup_logging(True)


def test_processor():
    """Test the MedspacyUmlsProcessor with sample data."""

    max_workers = min(psutil.cpu_count(logical=False) or 4, 10)
    logger.info(f"Using {max_workers} worker processes")

    with Manager() as manager:

        document_batch_inqueue = manager.Queue()
        nlp_results_outqueue = manager.Queue()
        halt_event = manager.Event()

        # right now this is only loading the batch_size, needs to fix
        reader_process = Process(
            target=FileSystemReader,
            kwargs={
                "path": "/test_data",
                "batch_size": 100,
                "extensions": [".txt"],
                "document_batch_inqueue": document_batch_inqueue,
                "user_interrupt": halt_event,
                "verbose": True,
            },
        )

        reader_process.start()

        #################################################################################
        # Process batches in parallel using a process pool
        #################################################################################

        num_processors_to_create = 1

        nlp_processes = [
            Process(
                target=QuickUMLSProcessor,
                kwargs={
                    "processor_id": 0,
                    "metric": "jaccard",
                    "document_batch_inqueue": document_batch_inqueue,
                    "nlp_results_outqueue": nlp_results_outqueue,
                    "process_interrupt": halt_event,
                },
            )
            for idx in range(num_processors_to_create)
        ]

        for p in nlp_processes:
            p.start()

        nlp_results_writer_process = Process(
            target=SQLiteNLPWriter,
            kwargs={
                "db_path": "/output/results.db",
                "nlp_results_outqueue": nlp_results_outqueue,
                "user_interrupt": halt_event,
                "verbose": True,
            },
        )

        nlp_results_writer_process.start()

        reader_process.join()
        all(x.join() for x in nlp_processes)
        nlp_results_writer_process.join()

        logger.info("All processes have joined")

        logger.success("Test Complete")


if __name__ == "__main__":
    freeze_support()
    logger.info("QuickUMLSProcessor Test")
    logger.info("=" * 50)
    test_processor()
