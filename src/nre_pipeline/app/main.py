"""
Main module for the NRE Pipeline.

This module contains the core functionality for processing non-routine events.
"""

from typing import Any, Dict

from loguru import logger

from nre_pipeline import setup_logging
from nre_pipeline.pipeline._manager import PipelineManager
from nre_pipeline.processor.noop_processor import NoOpProcessor
from nre_pipeline.reader import FileSystemReader
from nre_pipeline.writer.database._sqlite_writer import SQLiteNLPWriter


def run(args: Any) -> int:
    """
    Main entry point for the NRE Pipeline.

    Args:
        args: Command line arguments parsed by argparse

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    setup_logging(args.verbose)

    logger.info("Starting NRE Pipeline...")

    try:
        with PipelineManager(
            num_processor_workers=4,
            processor=NoOpProcessor,
            reader=lambda: FileSystemReader(
                input_paths=r"Z:\_\data\corpora\ocred_docs_from_pubmed",
                doc_batch_size=1000,
                allowed_extensions=[".txt"],
            ),
            writer=SQLiteNLPWriter,
        ) as manager:
            manager.run()
        logger.info("Pipeline completed successfully.")
        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return 1


def process_events(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process non-routine events data.

    Args:
        data: Input data containing events to process

    Returns:
        Dict containing processed results
    """
    # Placeholder for event processing logic
    logger.info("Processing events...")

    # Add your event processing logic here
    processed_data = {
        "status": "processed",
        "events_count": len(data.get("events", [])),
        "results": [],
    }

    return processed_data
