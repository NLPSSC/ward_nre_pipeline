#!/usr/bin/env python3
"""
Simple test for MedspacyUmlsProcessor to debug the matching issue.
"""


from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager, Process
import os
from typing import Iterator, List

import psutil


from nre_pipeline.common import setup_logging
from nre_pipeline.models._nlp_result import NLPResultFeatures
from nre_pipeline.processor._base import ProcessorProcess, ProcessorQueue
from nre_pipeline.processor.quickumls_processor._quickumls import QuickUMLSProcessor


from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._document import Document
from nre_pipeline.reader._filesystem import FileSystemReader

logger = setup_logging(False)


def test_processor():
    """Test the MedspacyUmlsProcessor with sample data."""

    max_workers = min(psutil.cpu_count(logical=False) or 4, 10)
    logger.info(f"Using {max_workers} worker processes")

    with Manager() as manager:

        processing_queue = manager.Queue()
        halt_event = manager.Event()

        reader = FileSystemReader(
            path="/test_data",
            batch_size=10,
            extensions=[".txt"],
        )

        #################################################################################
        # Process batches in parallel using a process pool
        #################################################################################

        num_processors_to_create = 1

        quickumls_process = ProcessorProcess(QuickUMLSProcessor, processor_id=0, queue=processing_queue, process_interrupt=halt_event)
        
        quickumls_process()

if __name__ == "__main__":
    logger.info("QuickUMLSProcessor Test")
    logger.info("=" * 50)
    test_processor()
