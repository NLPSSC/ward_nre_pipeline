"""
FileSystemReader class for recursively iterating over files in a directory.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List


class FileSystemReader:
    """
    A class that provides recursive iteration over files in a filesystem directory.

    Attributes:
        path (Path): The root path to iterate from
        exclude (list[Path]): List of paths/patterns to exclude from iteration
    """

    def __init__(
        self,
        path: List[str | Path] | Path | str,
        extensions: List[str] | None = None,
        exclude: list[str | Path] | None = None,
    ):
        """
        Initialize the FileSystemReader with a path.

        Args:
            path: The directory path to read from
            exclude: List of paths/patterns to exclude from iteration

        Raises:
            ValueError: If the path doesn't exist or is not a directory
        """
        if isinstance(path, (str, Path)):
            self._path: List[Path] = [Path(path)]
        else:
            self._path: List[Path] = [Path(p) for p in path]
        self._extensions: List[str] | None = extensions
        self._exclude: List[Path] = [Path(p) for p in (exclude or [])]

        for p in self._path:
            if not p.exists():
                raise ValueError(f"Path does not exist: {p}")

            if not p.is_dir():
                raise ValueError(f"Path is not a directory: {p}")

    def __iter__(self):
        """
        Return an iterator that yields files recursively.

        Yields:
            Path: Each file found in the directory tree
        """
        for p in self._path:
            for root, dirs, files in os.walk(p):
                root_path = Path(root)
                for file in files:
                    file_path: Path = root_path / file
                    if not self._is_excluded(file_path):
                        yield file_path

    def iter_notes(self, pattern: str = "*"):
        """
        Iterate over files matching a specific pattern.

        Args:
            pattern: Glob pattern to match files (default: "*")

        Yields:
            Path: Each file matching the pattern
        """
        for file_path in self:
            if file_path.match(pattern):
                yield file_path

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
