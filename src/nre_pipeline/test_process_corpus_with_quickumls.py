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

logger = setup_logging(verbose=True)


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
    permitted_extensions = [".txt"]
    reader_is_verbose = True

    with Manager() as manager:

        document_batch_inqueue = _create_inqueue(manager)
        nlp_results_outqueue = _create_outqueue(manager)
        halt_event = manager.Event()

        reader_process = initialize_reader(
            FileSystemReader,
            permitted_extensions,
            reader_is_verbose,
            document_batch_inqueue,
            halt_event,
        )

        # if _get_runstate() == "reader_only":
        #     assert test_reader(document_batch_inqueue) == _get_max_notes_to_process()
        #     logger.success("Reader-only test complete")
        #     sys.exit(0)

        nlp_processes: List[Process] = initialize_nlp_processes(
            processor_type=QuickUMLSProcessor,
            document_batch_inqueue=document_batch_inqueue,
            nlp_results_outqueue=nlp_results_outqueue,
            halt_event=halt_event,
        )

        nlp_results_writer_process: Process = initialize_writer_process(
            writer_type=SQLiteNLPWriter,
            nlp_results_outqueue=nlp_results_outqueue,
            halt_event=halt_event,
            use_strategy=ResetEachUseStrategy(),
            writer_is_verbose=True,
        )

        wait_for_all_to_finish(
            reader_process, nlp_processes, nlp_results_writer_process
        )

        logger.success("Complete")


def wait_for_all_to_finish(reader_process, nlp_processes, nlp_results_writer_process):
    reader_process.join()
    all(x.join() for x in nlp_processes)
    nlp_results_writer_process.join()
    logger.info("All processes have joined")


def initialize_writer_process(
    writer_type,
    nlp_results_outqueue,
    halt_event,
    use_strategy,
    writer_is_verbose,
) -> Process:

    nlp_results_writer_process = Process(
        target=writer_type,
        kwargs={
            "db_path": _get_output_db(),
            "nlp_results_outqueue": nlp_results_outqueue,
            "user_interrupt": halt_event,
            "init_strategy": use_strategy,
            "verbose": writer_is_verbose,
        },
    )

    nlp_results_writer_process.start()

    return nlp_results_writer_process


def _get_output_db() -> str:
    results_path = os.getenv("RESULTS_PATH", None)
    if results_path is None:
        raise RuntimeError("RESULTS_PATH path not set")
    return results_path


def initialize_nlp_processes(
    processor_type, document_batch_inqueue, nlp_results_outqueue, halt_event
) -> List[Process]:
    nlp_processes: List[Process] = [
        Process(
            target=processor_type,
            kwargs=build_processor_config(
                idx, document_batch_inqueue, nlp_results_outqueue, halt_event
            ),
        )
        for idx in range(_get_num_processors_to_create())
    ]

    for p in nlp_processes:
        p.start()

    return nlp_processes


def build_processor_config(
    idx, document_batch_inqueue, nlp_results_outqueue, halt_event
):
    return {
        "processor_id": idx,
        "metric": "jaccard",
        "document_batch_inqueue": document_batch_inqueue,
        "nlp_results_outqueue": nlp_results_outqueue,
        "process_interrupt": halt_event,
    }


def initialize_reader(
    reader_type,
    permitted_extensions,
    reader_is_verbose,
    document_batch_inqueue,
    halt_event,
) -> Process:
    reader_process = Process(
        target=reader_type,
        kwargs=build_file_system_reader_config(
            permitted_extensions,
            reader_is_verbose,
            document_batch_inqueue,
            halt_event,
            get_input_data(),
        ),
    )
    reader_process.start()
    return reader_process


def build_file_system_reader_config(
    permitted_extensions,
    reader_is_verbose,
    document_batch_inqueue,
    halt_event,
    input_data_path,
):
    return {
        "path": input_data_path,
        "doc_batch_size": _get_reader_max_doc_per_batch(),
        "extensions": permitted_extensions,
        "document_batch_inqueue": document_batch_inqueue,
        "user_interrupt": halt_event,
        "verbose": reader_is_verbose,
        "debug_config": _initialize_debug_config(),
    }


def _create_outqueue(manager):
    return manager.Queue(maxsize=_get_outqueue_max_docbatch_count())


def _create_inqueue(manager):
    return manager.Queue(maxsize=_get_inqueue_max_docbatch_count())


def _get_runstate():
    return "full_test"


def _get_num_processors_to_create():
    num_processors_to_create = int(
        os.getenv("NUM_PROCESSORS_TO_CREATE", multiprocessing.cpu_count())
    )
    logger.debug("NUM_PROCESSORS_TO_CREATE: {}", num_processors_to_create)
    return num_processors_to_create


def _get_inqueue_max_docbatch_count():
    inqueue_max_docbatch_count = int(os.getenv("INQUEUE_MAX_DOCBATCH_COUNT", 1))
    logger.debug("INQUEUE_MAX_DOCBATCH_COUNT: {}", inqueue_max_docbatch_count)
    return inqueue_max_docbatch_count


def _get_outqueue_max_docbatch_count():
    outqueue_max_docbatch_count = int(os.getenv("OUTQUEUE_MAX_DOCBATCH_COUNT", 1))
    logger.debug("OUTQUEUE_MAX_DOCBATCH_COUNT: {}", outqueue_max_docbatch_count)
    return outqueue_max_docbatch_count


def _get_reader_max_doc_per_batch():
    reader_max_doc_per_batch = int(os.getenv("READER_MAX_DOC_PER_BATCH", 10))
    logger.debug("READER_MAX_DOC_PER_BATCH: {}", reader_max_doc_per_batch)
    return reader_max_doc_per_batch


def _initialize_debug_config():
    debug_config = {"max_notes_to_read": _get_max_notes_to_process()}
    logger.debug("max_notes_to_read: {}", debug_config["max_notes_to_read"])
    return debug_config


def _get_max_notes_to_process():
    debug_max_notes_to_process = os.getenv("DEBUG_MAX_NOTES_TO_PROCESS", None)
    if debug_max_notes_to_process is None:
        return None
    return int(debug_max_notes_to_process)


def get_input_data():
    input_data = os.getenv("INPUT_DATA_PATH")
    if not input_data:
        raise ValueError("INPUT_DATA_PATH environment variable is not set")
    input_data_path = Path(input_data)
    logger.debug("Input data path: {}", input_data_path)
    return input_data_path


if __name__ == "__main__":
    freeze_support()
    logger.info("QuickUMLSProcessor Test")
    logger.info("=" * 50)
    test_processor()
