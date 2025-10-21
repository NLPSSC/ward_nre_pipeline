#!/usr/bin/env python3
"""
Simple test for MedspacyUmlsProcessor to debug the matching issue.
"""

import multiprocessing
import os
from pathlib import Path

import random
import sys
from threading import Thread
from time import sleep
import psutil

from multiprocessing import Manager, Process, freeze_support
import queue
from typing import Dict, List, Literal, Union, cast
from nre_pipeline.common import setup_logging
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.processor._base import QUEUE_EMPTY, ProcessorQueue
from nre_pipeline.processor.quickumls_processor._quickumls import QuickUMLSProcessor
from nre_pipeline.reader._filesystem_reader import FileSystemReader
from nre_pipeline.writer.database._sqlite_writer import SQLiteNLPWriter
from nre_pipeline.writer.init_strategy import ResetEachUseStrategy

logger = setup_logging(True)


def test_reader(document_batch_inqueue) -> int:
    ##############################################################################
    # Testing the total count in reader
    ##############################################################################
    doc_list = []
    from nre_pipeline.models._document import Document

    try:
        while True:
            try:
                item = document_batch_inqueue.get(block=True, timeout=1)
            except queue.Empty:
                continue
            if item == QUEUE_EMPTY:
                break
            if item is not None:
                doc_list.extend(cast(List[Document], cast(DocumentBatch, item)[:]))
    except:
        pass
    finally:
        logger.debug("Total document count: %d", len(doc_list))
    return len(doc_list)


def test_processor():
    """Test the MedspacyUmlsProcessor with sample data."""

    max_workers = min(psutil.cpu_count(logical=False) or 4, 10)
    logger.info(f"Using {max_workers} worker processes")
    input_data_path = get_input_data()

    run_state: Literal["reader_only", "full_test"] = "full_test"

    INQUEUE_MAX_DOCBATCH_COUNT: int = 1
    NUM_PROCESSORS_TO_CREATE: int = 1
    OUTQUEUE_MAX_DOCBATCH_COUNT: int = 1
    READER_MAX_DOC_PER_BATCH: int = 10

    DEBUG_CONFIG: Union[Dict[str, int], None] = {
        "max_notes_to_read": 1000 or (READER_MAX_DOC_PER_BATCH * random.randint(1, 5) * (READER_MAX_DOC_PER_BATCH % 17) * random.randint(1, 3))
    }

    logger.debug("READER_MAX_DOC_PER_BATCH: {}", READER_MAX_DOC_PER_BATCH)
    logger.debug("max_notes_to_read: {}", DEBUG_CONFIG["max_notes_to_read"])

    with Manager() as manager:

        document_batch_inqueue = manager.Queue(maxsize=INQUEUE_MAX_DOCBATCH_COUNT)
        halt_event = manager.Event()

        # right now this is only loading the batch_size, needs to fix
        reader_process = Process(
            target=FileSystemReader,
            kwargs={
                "path": input_data_path,
                "doc_batch_size": READER_MAX_DOC_PER_BATCH,
                "extensions": [".txt"],
                "document_batch_inqueue": document_batch_inqueue,
                "user_interrupt": halt_event,
                "verbose": True,
                "debug_config": DEBUG_CONFIG,
            },
        )

        reader_process.start()

        if run_state == "reader_only":
            assert (
                test_reader(document_batch_inqueue) == DEBUG_CONFIG["max_notes_to_read"]
            )
            logger.success("Reader-only test complete")
            sys.exit(0)

        
        nlp_results_outqueue = manager.Queue(maxsize=OUTQUEUE_MAX_DOCBATCH_COUNT)
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
            for idx in range(NUM_PROCESSORS_TO_CREATE)
        ]

        for p in nlp_processes:
            p.start()

        nlp_results_writer_process = Process(
            target=SQLiteNLPWriter,
            kwargs={
                "db_path": "/output/results.db",
                "nlp_results_outqueue": nlp_results_outqueue,
                "user_interrupt": halt_event,
                # "init_strategy": ResetEachUseStrategy(),
                "verbose": True,
            },
        )

        nlp_results_writer_process.start()

        reader_process.join()
        all(x.join() for x in nlp_processes)
        nlp_results_writer_process.join()

        logger.info("All processes have joined")

        logger.success("Test Complete")


def get_input_data():
    input_data = os.getenv("INPUT_DATA_PATH")
    if not input_data:
        raise ValueError("INPUT_DATA_PATH environment variable is not set")
    input_data_path = Path(input_data)
    return input_data_path


if __name__ == "__main__":
    freeze_support()
    logger.info("QuickUMLSProcessor Test")
    logger.info("=" * 50)
    test_processor()
