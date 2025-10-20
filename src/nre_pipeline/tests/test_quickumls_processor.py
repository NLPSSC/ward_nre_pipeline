#!/usr/bin/env python3
"""
Simple test for MedspacyUmlsProcessor to debug the matching issue.
"""

from multiprocessing import Manager
import os


from nre_pipeline.common import setup_logging
from nre_pipeline.models._nlp_result import NLPResultFeatures
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
        processing_queue = manager.Queue()
        halt_event = manager.Event()

        try:
            # Initialize the processor
            processor = QuickUMLSProcessor(
                processor_id=0,
                metric="levenshtein",
                queue=processing_queue,
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
            batch = DocumentBatch(documents=test_documents)

            # Process the batch
            logger.info(f"\nProcessing batch with {len(test_documents)} documents...")
            processor_queue: ProcessorQueue = processor(batch)

            nlp_results: list[NLPResultFeatures] = list(
                [x for x in processor_queue.next_result()]
            )
            assert nlp_results, "No results found"
            assert all(
                len(result.result_features) > 0 for result in nlp_results
            ), "All results are empty"

            for nlp_result_features in nlp_results:
                logger.info(
                    f"  Document {nlp_result_features.note_id}: {len(nlp_result_features.result_features)} items"
                )
                logger.info(nlp_result_features.to_dict())

        except Exception as e:
            logger.error("Error during processing: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    logger.info("MedspacyUmlsProcessor Test")
    logger.info("=" * 50)
    test_processor()
