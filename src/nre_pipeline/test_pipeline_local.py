#!/usr/bin/env python3
"""
Test the MedspacyUmlsProcessor with the pipeline using local test data.
"""

import os
import sqlite3
import sys
from pathlib import Path

# Add src to path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger

from nre_pipeline import setup_logging
from nre_pipeline.pipeline._manager import PipelineManager
from nre_pipeline.processor._quickumls import QuickUMLSProcessor
from nre_pipeline.reader._filesystem import FileSystemReader
from nre_pipeline.writer.database._sqlite import SQLiteNLPWriter


def run_test() -> int:
    """Run the pipeline test with local data."""

    # Set up environment
    project_root = Path(__file__).parent
    quickumls_path = project_root / "quickumls"
    test_data_path = project_root / "test_data"

    os.environ["QUICKUMLS_PATH"] = str(quickumls_path)
    logger.info(f"Set QUICKUMLS_PATH to: {quickumls_path}")

    # Setup logging
    setup_logging(True)

    # Create temporary database
    temp_db_path = project_root / ".data" / "temp" / "pipeline_test.db"
    temp_db_path.parent.mkdir(parents=True, exist_ok=True)
    if temp_db_path.exists():
        temp_db_path.unlink()

    # Count files
    file_count = sum(1 for _ in test_data_path.rglob("*.txt"))
    logger.info(f"Found {file_count} .txt files in {test_data_path}")

    try:
        logger.info("Starting pipeline test...")

        with PipelineManager(
            num_processor_workers=2,
            processor=QuickUMLSProcessor,
            reader=FileSystemReader.create_reader(
                path=str(test_data_path),
                batch_size=10,
                extensions=[".txt"],
            ),
            writer=SQLiteNLPWriter.create_writer(db_path=str(temp_db_path.resolve())),
        ) as manager:
            manager.run()
            database_path = manager.writer_details()["database_path"]

        logger.info(
            f"Pipeline completed successfully; output written to database: {database_path}"
        )

        # Check results in database
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()

            # Count documents processed
            cursor.execute("SELECT COUNT(DISTINCT note_id) FROM nlp_notes")
            doc_count = cursor.fetchone()[0]
            logger.info(f"Number of distinct documents processed: {doc_count}")

            # Count total results
            cursor.execute("SELECT COUNT(*) FROM nlp_notes")
            result_count = cursor.fetchone()[0]
            logger.info(f"Total number of NLP results: {result_count}")

            # Show sample results
            cursor.execute("""
                SELECT note_id, key, value 
                FROM nlp_notes 
                WHERE key = 'term' 
                LIMIT 10
            """)
            sample_results = cursor.fetchall()

            logger.info("Sample results:")
            for note_id, key, value in sample_results:
                logger.info(f"  {note_id}: {value}")

            if result_count == 0:
                logger.warning("⚠️  No results found in database!")
                return 1
            else:
                logger.success(
                    f"✓ Pipeline test successful! Found {result_count} results."
                )
                return 0

    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    print("Pipeline Test with MedspacyUmlsProcessor")
    print("=" * 50)
    exit_code = run_test()
    sys.exit(exit_code)
