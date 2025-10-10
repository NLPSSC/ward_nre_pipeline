"""
FileSystemReader class for recursively iterating over files in a directory.
"""

from __future__ import annotations

import multiprocessing
import os
from pathlib import Path
from typing import Any, Callable, Generator, List

from loguru import logger

from nre_pipeline.models import Document
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.reader._base import CorpusReader


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
        batch_size: int,
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
            batch_size=batch_size, allow_batch_resize=allow_batch_resize, **kwargs
        )

        if isinstance(path, (str, Path)):
            self._path: List[Path] = [Path(path)]
        else:
            self._path: List[Path] = [Path(p) for p in path]

        if batch_size < 1:
            raise ValueError("Batch size must be at least 1")
        self._batch_size: int = batch_size
        self._extensions: List[str] | None = extensions
        self._exclude: List[Path] = [Path(p) for p in (exclude or [])]

        for p in self._path:
            if not p.exists():
                raise ValueError(f"Path does not exist: {p}")

            if not p.is_dir():
                raise ValueError(f"Path is not a directory: {p}")

    def _batch_resize(self, num_processor_workers: int) -> int | None:
        total_file_count = sum(1 for _ in self._files_to_process_iter())
        new_batch_size = (total_file_count // num_processor_workers) + 1
        return new_batch_size

    def _iter(self) -> Generator[DocumentBatch, Any, None]:
        """
        Return an iterator that yields files recursively.

        Yields:
            Path: Each file found in the directory tree
        """

        # All files in all paths
        files = self._files_to_process_iter()
        # Filter files by extension and exclusion patterns
        filtered_files = (self.make_doc(f) for f in files if not self._is_excluded(f))
        iteration_number = 0
        while True:
            iteration_number += 1
            batch: List[Document] = [
                doc for _, doc in zip(range(self._batch_size), filtered_files)
            ]
            if not batch:
                break
            document_batch = DocumentBatch(batch)
            logger.debug(
                "Loading batch # {}, iteration {}",
                document_batch.batch_id,
                iteration_number,
            )
            yield document_batch

    def _files_to_process_iter(self):
        return (
            (Path(root) / f)
            for p in self._path
            for root, dirs, files in os.walk(p)
            for f in files
        )

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
            batch_size=batch_size,
            extensions=extensions,
            exclude=exclude,
        )
