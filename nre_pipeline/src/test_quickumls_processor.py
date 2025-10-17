#!/usr/bin/env python3
"""
Simple test for MedspacyUmlsProcessor to debug the matching issue.
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger

from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.models._document import Document
from nre_pipeline.processor._medspacy_umls import MedspacyUmlsProcessor


def test_processor():
    """Test the MedspacyUmlsProcessor with sample data."""

    # Set the environment variable
    os.environ["QUICKUMLS_PATH"] = str(Path(__file__).parent / "quickumls")

    print(f"QUICKUMLS_PATH set to: {os.environ['QUICKUMLS_PATH']}")

    # Enable debug logging
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    try:
        # Initialize the processor
        processor = MedspacyUmlsProcessor(processor_id=0)
        print("✓ Processor initialized successfully")

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
        print(f"\nProcessing batch with {len(test_documents)} documents...")
        results = list(processor._call(batch))

        print(f"\nProcessing completed. Found {len(results)} results:")
        for result in results:
            print(f"  Document {result.note_id}: {len(result.results)} items")
            for item in result.results[:3]:  # Show first 3 items
                if item.key == "term":
                    print(f"    - {item.value}")

        if not results:
            print("⚠️  No results found!")
        elif all(len(result.results) == 0 for result in results):
            print("⚠️  All results are empty!")
        else:
            print("✓ Processing successful with results")

    except Exception as e:
        print(f"✗ Error during processing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("MedspacyUmlsProcessor Test")
    print("=" * 50)
    test_processor()
