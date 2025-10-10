import os
from pathlib import Path
import tempfile
from typing import Any

from loguru import logger
from nre_pipeline import setup_logging
from nre_pipeline.pipeline._manager import PipelineManager
from nre_pipeline.processor._medspacy_umls import MedspacyUmlsProcessor
from nre_pipeline.processor._noop import NoOpProcessor
from nre_pipeline.reader._filesystem import FileSystemReader
from nre_pipeline.writer.database._sqlite import SQLiteNLPWriter
import sqlite3


def run() -> int:
    """
    Main entry point for the NRE Pipeline.

    Args:
        args: Command line arguments parsed by argparse

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    setup_logging(True)

    logger.info("Starting NRE Pipeline...")
    test_case_path = (
        r"Z:\_\data\corpora\ocred_docs_from_pubmed\Buffalo_Med_J_Mon_Rev_Med_Surg_Sci"
    )
    file_count = sum(1 for _ in Path(test_case_path).rglob("*.txt"))
    logger.info(f"Found {file_count} .txt files in {test_case_path}")
    temp_db_path = Path(
        r"Z:\_\active\nlpssc\project_ward_non-routine_events\nre_pipeline\.data\temp\test.db"
    )
    temp_db_path.parent.mkdir(exist_ok=True)
    if temp_db_path.exists():
        temp_db_path.unlink()

    try:
        with PipelineManager(
            num_processor_workers=4,
            processor=MedspacyUmlsProcessor,
            reader=FileSystemReader.create_reader(
                path=test_case_path,
                batch_size=1000,
                extensions=[".txt"],
            ),
            writer=SQLiteNLPWriter.create_writer(db_path=str(temp_db_path.resolve())),
        ) as manager:
            manager.run()
            database_path = manager.writer_details()["database_path"]
        logger.info(
            f"Pipeline completed successfully; output written to database: {database_path}"
        )
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT note_id) FROM nlp_notes")
            count = cursor.fetchone()[0]
        logger.info(f"Number of distinct note_id in database: {count}")
        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    run()
