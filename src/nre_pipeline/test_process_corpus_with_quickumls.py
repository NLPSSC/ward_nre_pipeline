#!/usr/bin/env python3
"""
Simple test for MedspacyUmlsProcessor to debug the matching issue.
"""


from multiprocessing import Manager, Process, freeze_support
import queue
from typing import List, cast
from nre_pipeline.common import setup_logging
from nre_pipeline.common.base._base_processor import initialize_nlp_processes
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.common.base._base_processor import QUEUE_EMPTY
from nre_pipeline.processor.quickumls_processor._quickumls import (
    QuickUMLSProcessor,
    build_quickumls_processor_config,
)
from nre_pipeline.queues import (
    _create_inqueue,
    _create_outqueue,
)
from nre_pipeline.reader._filesystem_reader import (
    FileSystemReader,
    build_file_system_reader_config,
)
from nre_pipeline.reader._filesystem_reader import initialize_reader
from nre_pipeline.writer.database._sqlite_writer import (
    SQLiteNLPWriter,
    build_sqlite_configuration,
)
from nre_pipeline.writer.database._sqlite_writer import initialize_writer_process
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
            config=build_file_system_reader_config(
                permitted_extensions,
                reader_is_verbose,
                document_batch_inqueue,
                halt_event,
            ),
        )

        # if _get_runstate() == "reader_only":
        #     assert test_reader(document_batch_inqueue) == _get_max_notes_to_process()
        #     logger.success("Reader-only test complete")
        #     sys.exit(0)

        nlp_processes, processing_barrier = initialize_nlp_processes(
            processor_type=QuickUMLSProcessor,
            config=build_quickumls_processor_config(
                document_batch_inqueue, nlp_results_outqueue, halt_event
            ),
            manager=manager,
        )

        nlp_results_writer_process: Process = initialize_writer_process(
            writer_type=SQLiteNLPWriter,
            config=build_sqlite_configuration(
                nlp_results_outqueue,
                halt_event,
                use_strategy=ResetEachUseStrategy(),
                writer_is_verbose=True,
                processing_barrier=processing_barrier,
            ),
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


def _get_runstate():
    return "full_test"


if __name__ == "__main__":
    freeze_support()
    logger.info("QuickUMLSProcessor Test")
    logger.info("=" * 50)
    test_processor()
