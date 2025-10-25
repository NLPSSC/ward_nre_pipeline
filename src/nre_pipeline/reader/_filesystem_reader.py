"""
FileSystemReader class for recursively iterating over files in a directory.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Generator, List, Union

from loguru import logger

from nre_pipeline.models import Document
from nre_pipeline.models._batch import DocumentBatch, DocumentBatchBuilder
from nre_pipeline.common.base._base_reader import CorpusReader
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
        input_paths: List[str | Path] | Path | str,
        allowed_extensions: List[str] | None = None,
        excluded_paths: List[str | Path] | None = None,
        **config,
    ) -> None:
        super().__init__(**config)

        ################################################################
        # Path initialization and validation
        ################################################################
        self._path: List[Path] = self._normalize_input_paths(input_paths)

        ################################################################
        # Accepted Extensions
        ################################################################
        self._extensions: List[str] | None = allowed_extensions

        ################################################################
        # Excluded Paths
        ################################################################
        self._exclude: List[Path] = self._normalize_excluded_paths(excluded_paths)

        self._debug_log("FileSystemReader loaded")

    def get_process_name(self):
        return f"FileSystemReader"

    def make_doc(self, source: Path | str) -> Document:
        """Create a Document from a file path.

        Args:
            source (Path | str): The file path to read from.

        Raises:
            ValueError: If the source is not a valid file path.

        Returns:
            Document: The created Document object.
        """

        source_path: Path = self._normalize_source(source)
        note_id: str = self._get_note_id(source_path)
        return self._read_document(source_path, note_id)

    def _read_document(self, source_path, note_id) -> Document:
        """Reads a document from the filesystem.

        Args:
            source_path (Path): The path to the source file.
            note_id (str): The ID of the note.

        Returns:
            Document: The created Document object.
        """
        try:
            valid_document = True
            # Optimized file reading with larger buffer and binary mode for better performance
            with open(
                source_path, "r", encoding="utf-8", errors="ignore", buffering=8192
            ) as f:
                text = f.read()
        except Exception as e:
            logger.error(f"Error reading file {source_path}: {e}")
            text = ""  # Return empty string rather than failing
            valid_document = False

        document: Document = Document(
            note_id=note_id,
            text=text,
            valid=valid_document,
            metadata={"path": str(source_path)},
        )
        return document

    def _normalize_source(self, source) -> Path:
        """Normalize the source input to a Path object.

        Args:
            source (Union[str, Path]): The source input to normalize.

        Raises:
            ValueError: If the source is not a valid file path.

        Returns:
            Path: The normalized Path object.
        """
        if isinstance(source, (Path, str)) is False:
            raise ValueError("Source must be a Path or string representing a file path")
        if os.path.exists(source) is False:
            raise ValueError("Source file does not exist")
        source_path = Path(source)
        return source_path

    def _get_note_id(self, source_path: Path) -> str:
        """Get the note ID from the source path.

        Args:
            source_path (Path): The path to the source file.

        Returns:
            str: The ID of the note.
        """
        return source_path.stem

    def _normalize_excluded_paths(self, excluded_paths) -> List[Path]:
        """Normalize excluded paths to a list of Path objects.

        Args:
            excluded_paths (Union[str, Path, List[Union[str, Path]]]): The excluded paths to normalize.

        Returns:
            List[Path]: A list of normalized Path objects
        """
        return [Path(p) for p in (excluded_paths or [])]

    def _normalize_input_paths(self, input_paths) -> List[Path]:
        """Normalize input paths to a list of Path objects.

        Args:
            input_paths (Union[str, Path, List[Union[str, Path]]]): The input paths to normalize.

        Raises:
            ValueError: If any path does not exist or is not a directory

        Returns:
            List[Path]: A list of normalized Path objects
        """
        if isinstance(input_paths, (str, Path)):
            paths: List[Path] = [Path(input_paths)]
        else:
            paths = [Path(p) for p in input_paths]
        for p in paths:
            if not p.exists():
                raise ValueError(f"Path does not exist: {p}")

            if not p.is_dir():
                raise ValueError(f"Path is not a directory: {p}")
        return paths

    def _get_file_count(self) -> int:
        """Get the total number of files to process.

        Returns:
            int: The total number of files to process.
        """
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
            batch = batch_builder.build()
            total_documents += len(batch)
            yield batch

        logger.info("Total Documents Read: {}", total_documents)

    def _files_to_process_iter(self) -> Generator[Path, Any, None]:
        """Yield files to process from the input paths.

        Yields:
            Generator[Path, Any, None]: The file paths to process.
        """
        for p in self._path:
            for root, _, files in os.walk(p):
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


########################################################
# Used later for batch resize
########################################################
# allow_batch_resize: bool = True,
# def _batch_resize(self, num_processor_workers: int) -> int | None:
#     total_file_count = self._get_file_count()
#     new_batch_size = (total_file_count // num_processor_workers) + 1
#     return new_batch_size


########################################################
# Needed if need indirect method to create a reader
########################################################
# @staticmethod
# def create_reader(**kwargs) -> Callable[[], CorpusReader]:
#     path = kwargs.get("path", None)
#     batch_size = kwargs.get("batch_size", 1000)
#     extensions = kwargs.get("extensions", None)
#     exclude = kwargs.get("exclude", None)
#     if path is None:
#         raise ValueError("Path must be provided.")
#     if batch_size is None:
#         raise ValueError("Batch size must be provided.")
#     # if extensions is None:
#     #     raise ValueError("Extensions must be provided.")
#     # if exclude is None:
#     #     raise ValueError("Exclude must be provided.")
#     return lambda: FileSystemReader(
#         input_paths=path,
#         doc_batch_size=batch_size,
#         allowed_extensions=extensions,
#         excluded_paths=exclude,
#     )

########################################################
# Indirect method to create config for reader
########################################################
# @staticmethod
# def build_file_system_reader_config(
#     permitted_extensions: List[str],
#     document_batch_inqueue: queue.Queue,
#     halt_event: threading.Event,
# ) -> Dict[str, Any]:
#     # "doc_batch_size": _get_NUMBER_DOCS_TO_READ_BEFORE_YIELD(),
#     # "debug_config": _initialize_read_debug_config(),
#     return {
#         "path": _get_input_data(),
#         "extensions": permitted_extensions,
#         "document_batch_inqueue": document_batch_inqueue,
#         "user_interrupt": halt_event,
#         "verbose": _get_reader_verbosity(),
#     }

# def _get_reader_verbosity() -> bool:
#     verbose_reader = os.getenv("VERBOSE_READER")
#     if verbose_reader is None:
#         logger.warning("VERBOSE_READER not set, defaulting to False")
#         verbose_reader = "False"
#     return verbose_reader.lower() == "true"


# def _get_input_data():
#     input_data = os.getenv("INPUT_DATA_PATH")
#     if not input_data:
#         raise ValueError("INPUT_DATA_PATH environment variable is not set")
#     input_data_path = Path(input_data)
#     logger.debug("Input data path: {}", input_data_path)
#     return input_data_path

########################################################
# Only needed if not derived from Process
########################################################
# def initialize_reader(
#     reader_type,
#     config,
# ) -> Process:
#     reader_process = Process(
#         target=reader_type,
#         kwargs=config,
#     )
#     reader_process.start()
#     return reader_process
