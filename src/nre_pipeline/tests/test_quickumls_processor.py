#!/usr/bin/env python3
"""
Simple test for MedspacyUmlsProcessor to debug the matching issue.
"""

from multiprocessing import Manager
import os
import queue
from typing import List, cast


from nre_pipeline.common import setup_logging
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.processor._base import ProcessorQueue
from nre_pipeline.processor.quickumls_processor._quickumls import QuickUMLSProcessor


from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._document import Document

logger = setup_logging(False)


def test_processor():
    """Test the MedspacyUmlsProcessor with sample data."""

    # Set the environment variable

    quickumls_path = os.getenv("QUICKUMLS_PATH", None)
    if quickumls_path is None:
        raise ValueError("QUICKUMLS_PATH environment variable is not set.")

    with Manager() as manager:
        document_batch_inqueue = manager.Queue()
        nlp_results_outqueue = manager.Queue()
        halt_event = manager.Event()

        # Initialize the processor
        processor = QuickUMLSProcessor(
            processor_id=0,
            metric="cosine",
            document_batch_inqueue=document_batch_inqueue,
            nlp_results_outqueue=nlp_results_outqueue,
            process_interrupt=halt_event,
        )
        logger.success("Processor initialized successfully")

        # Create a test document with medical content
        test_documents = [
            Document(
                note_id="test_001",
                text="The patient has diabetes mellitus and hypertension.",
            ),
            Document(
                note_id="test_002",
                text="Patient presents with chest pain and shortness of breath.",
            ),
            Document(
                note_id="test_003",
                text="Diagnosis: acute myocardial infarction with pneumonia.",
            ),
        ]

        # Create a document batch
        test_doc_batch = DocumentBatch(documents=test_documents)

        ###############################################################################
        # Manually load document batch into the input queue
        ###############################################################################

        assert (
            document_batch_inqueue.qsize() == 0
        ), "Input queue should be empty before processing."

        document_batch_inqueue.put(test_doc_batch)

        assert (
            document_batch_inqueue.qsize() == 1
        ), "Input queue should have one item after adding batch."
        logger.debug("Number of batches in queue: {}", document_batch_inqueue.qsize())

        logger.debug("Manually adding ProcessorQueue.QUEUE_EMPTY...")
        document_batch_inqueue.put(ProcessorQueue.QUEUE_EMPTY)
        assert (
            document_batch_inqueue.qsize() == 2
        ), "Input queue should have two items after adding batch and empty marker."

        # Process the batch
        logger.info(f"\nProcessing batch with {len(test_documents)} documents...")

        ###############################################################################
        # Manually call processor
        ###############################################################################
        processor()

        nlp_result_items: List[NLPResultItem] = []

        try:
            while True:
                # ProcessorQueue.QUEUE_EMPTY
                try:
                    outqueue_item = nlp_results_outqueue.get(block=True, timeout=5)
                except queue.Empty:
                    continue

                if outqueue_item == ProcessorQueue.QUEUE_EMPTY:
                    break
                elif isinstance(outqueue_item, NLPResultItem):
                    nlp_result_item: NLPResultItem = cast(NLPResultItem, outqueue_item)
                    nlp_result_items.append(nlp_result_item)
                else:
                    raise RuntimeError("Unexpected item type in writer queue")

            assert (
                len(nlp_result_items) > 0
            ), "No results were returned by processor_queue.next_result()."

            note_ids = {n.note_id for n in nlp_result_items}

            assert len(note_ids) == len(test_documents), "Mismatch in document count."

        except Exception as e:
            logger.error(f"Unexpected error during processor test: {e}")
            raise
        else:
            logger.success("Test Complete")


if __name__ == "__main__":
    logger.info("QuickUMLSProcessor Test")
    logger.info("=" * 50)
    test_processor()
