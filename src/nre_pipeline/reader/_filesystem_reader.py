"""
FileSystemReader class for recursively iterating over files in a directory.
"""

from __future__ import annotations

from multiprocessing import Process
import os
from pathlib import Path
from typing import Any, Callable, Generator, List, Union

from loguru import logger

from nre_pipeline.models import Document
from nre_pipeline.models._batch import DocumentBatch, DocumentBatchBuilder
from nre_pipeline.common.base._base_reader import (
    CorpusReader,
    _get_reader_max_doc_per_batch,
    _initialize_read_debug_config,
)
from loguru import logger


class FileSystemReader(CorpusReader):
    """
    A class that provides recursive iteration over files in a filesystem directory.

    Inherits from CorpusReader to provide concrete implementation of file iteration.

    Attributes:
        path (List[Path]): The root paths to iterate from
        extensions (List[str] | None): List of file extensions to filter by
        exclude (List[Path]): List of paths/patterns to exclude from iteration
    """

    def __init__(
        self,
        path: List[str | Path] | Path | str,
        doc_batch_size: int,
        extensions: List[str] | None = None,
        exclude: list[str | Path] | None = None,
        allow_batch_resize: bool = True,
        **kwargs,
    ):
        """
        Initialize the FileSystemReader with a path.

        Args:
            path: The directory path to read from
            exclude: List of paths/patterns to exclude from iteration

        Raises:
            ValueError: If the path doesn't exist or is not a directory
        """

        super().__init__(
            doc_batch_size=doc_batch_size,
            allow_batch_resize=allow_batch_resize,
            **kwargs,
        )

        if isinstance(path, (str, Path)):
            self._path: List[Path] = [Path(path)]
        else:
            self._path: List[Path] = [Path(p) for p in path]

        if doc_batch_size < 1:
            raise ValueError("Batch size must be at least 1")
        self._extensions: List[str] | None = extensions
        self._exclude: List[Path] = [Path(p) for p in (exclude or [])]

        for p in self._path:
            if not p.exists():
                raise ValueError(f"Path does not exist: {p}")

            if not p.is_dir():
                raise ValueError(f"Path is not a directory: {p}")

        self._debug_log("FileSystemReader loaded")
        self.start()

    def _batch_resize(self, num_processor_workers: int) -> int | None:
        total_file_count = self._get_file_count()
        new_batch_size = (total_file_count // num_processor_workers) + 1
        return new_batch_size

    def _get_file_count(self):
        return sum(1 for _ in self._files_to_process_iter())

    def _iter(self) -> Generator[DocumentBatch, Any, None]:
        """
        Return an iterator that yields files recursively.

        Yields:
            DocumentBatch: Each batch of Document objects
        """
        files = self._files_to_process_iter()
        filtered_files = (self.make_doc(f) for f in files if not self._is_excluded(f))
        iteration_number = 0
        total_documents = 0
        batch_size = self._doc_batch_size

        batch_builder = DocumentBatchBuilder(batch_size)
        for ff in filtered_files:
            iteration_number += 1
            batch: Union[DocumentBatch, None] = batch_builder.add_document(ff)
            if batch is not None:
                total_documents += len(batch)
                yield batch
                batch_builder = DocumentBatchBuilder(batch_size)

        if batch_builder.has_docs():
            yield batch_builder.build()

        logger.info("Total Documents Read: {}", total_documents)

    def _files_to_process_iter(self):
        for p in self._path:
            for root, dirs, files in os.walk(p):
                for f in files:
                    yield Path(root) / f

    def _is_excluded(self, file_path: Path) -> bool:
        """
        Check if a file path should be excluded from iteration.

        Args:
            file_path: The file path to check

        Returns:
            bool: True if the file should be excluded, False otherwise
        """
        # Extension filtering: if self._extensions is not None, only allow files with allowed extensions
        if self._extensions is not None and len(self._extensions) > 0:
            if file_path.suffix.lower() not in {
                ext.lower() if ext.startswith(".") else "." + ext.lower()
                for ext in self._extensions
            }:
                return True

        for exclude_path in self._exclude:
            # Check if the file path matches the exclude pattern
            try:
                # Try exact match first
                if file_path.samefile(exclude_path):
                    return True
            except (OSError, FileNotFoundError):
                # If files don't exist, fall back to string/pattern matching
                pass

            # Check if it's a subdirectory of an excluded directory
            try:
                if exclude_path.is_dir() and file_path.is_relative_to(exclude_path):
                    return True
            except (OSError, ValueError):
                pass

            # Check pattern matching (glob-style)
            if file_path.match(str(exclude_path)):
                return True

        return False

    def make_doc(self, source: Any) -> Document:
        if isinstance(source, (Path, str)) is False:
            raise ValueError("Source must be a Path or string representing a file path")
        source_path = Path(source)
        note_id = source_path.stem

        # Optimized file reading with larger buffer and binary mode for better performance
        try:
            with open(
                source_path, "r", encoding="utf-8", errors="ignore", buffering=8192
            ) as f:
                text = f.read()
        except Exception as e:
            logger.error(f"Error reading file {source_path}: {e}")
            text = ""  # Return empty string rather than failing

        return Document(note_id=note_id, text=text, metadata={"path": str(source_path)})

    @staticmethod
    def create_reader(**kwargs) -> Callable[[], CorpusReader]:
        path = kwargs.get("path", None)
        batch_size = kwargs.get("batch_size", 1000)
        extensions = kwargs.get("extensions", None)
        exclude = kwargs.get("exclude", None)
        if path is None:
            raise ValueError("Path must be provided.")
        if batch_size is None:
            raise ValueError("Batch size must be provided.")
        # if extensions is None:
        #     raise ValueError("Extensions must be provided.")
        # if exclude is None:
        #     raise ValueError("Exclude must be provided.")
        return lambda: FileSystemReader(
            path=path,
            doc_batch_size=batch_size,
            extensions=extensions,
            exclude=exclude,
        )


def build_file_system_reader_config(
    permitted_extensions, reader_is_verbose, document_batch_inqueue, lock_folder
):
    return {
        "path": _get_input_data(),
        "doc_batch_size": _get_reader_max_doc_per_batch(),
        "extensions": permitted_extensions,
        "document_batch_inqueue": document_batch_inqueue,
        "verbose": reader_is_verbose,
        "debug_config": _initialize_read_debug_config(),
        "lock_folder": lock_folder,
    }


def _get_input_data():
    input_data = os.getenv("INPUT_DATA_PATH")
    if not input_data:
        raise ValueError("INPUT_DATA_PATH environment variable is not set")
    input_data_path = Path(input_data)
    logger.debug("Input data path: {}", input_data_path)
    return input_data_path


def initialize_reader(
    reader_type,
    config,
) -> Process:
    reader_process = Process(
        target=reader_type,
        kwargs=config,
    )
    reader_process.start()
    return reader_process
