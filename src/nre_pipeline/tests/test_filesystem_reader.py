"""
Tests for FileSystemReader class.
"""

import tempfile
from pathlib import Path

import pytest

from nre_pipeline.reader import FileSystemReader


def test_filesystem_reader_initialization():
    """Test FileSystemReader initialization with valid path."""
    # Use current directory as a test path
    current_dir = Path.cwd()
    reader = FileSystemReader(current_dir)
    assert reader._path == current_dir


def test_filesystem_reader_invalid_path():
    """Test FileSystemReader initialization with invalid path."""
    with pytest.raises(ValueError, match="Path does not exist"):
        FileSystemReader("/nonexistent/path")


def test_filesystem_reader_file_path():
    """Test FileSystemReader initialization with file instead of directory."""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile() as tmp:
        with pytest.raises(ValueError, match="Path is not a directory"):
            FileSystemReader(tmp.name)


def test_filesystem_reader_iteration():
    """Test that FileSystemReader can iterate over files."""
    # Use the tests directory itself
    tests_dir = Path(__file__).parent
    reader = FileSystemReader(tests_dir)

    files = list(reader)
    assert len(files) > 0
    assert all(isinstance(f, Path) for f in files)
    assert all(f.is_file() for f in files)




def test_filesystem_reader_with_exclude():
    """Test FileSystemReader with exclude parameter."""
    import os

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        # Create test files
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / "exclude_me.txt").touch()
        # Create subdirectory with files
        sub_dir = tmp_path / "subdir"
        sub_dir.mkdir()
        (sub_dir / "sub_file.txt").touch()
        # Test excluding specific file
        reader = FileSystemReader(
            [tmp_path], extensions=[".txt", ".py"], exclude=["exclude_me.txt"]
        )
        files = [f.name for f in reader]
        assert "exclude_me.txt" not in files
        assert "file1.txt" in files
        assert "file2.py" in files


def test_filesystem_reader_exclude_directory():
    """Test FileSystemReader excluding entire directories."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        # Create test structure
        (tmp_path / "keep.txt").touch()
        exclude_dir = tmp_path / "exclude_dir"
        exclude_dir.mkdir()
        (exclude_dir / "excluded_file.txt").touch()
        # Test excluding directory
        reader = FileSystemReader(tmp_path, exclude=[exclude_dir])
        files = list(reader)
        file_names = [f.name for f in files]
        assert "keep.txt" in file_names
        assert "excluded_file.txt" not in file_names


def test_filesystem_reader_exclude_pattern():
    """Test FileSystemReader with glob patterns in exclude."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        # Create test files
        (tmp_path / "test_file1.py").touch()
        (tmp_path / "test_file2.py").touch()
        (tmp_path / "keep_file.txt").touch()
        # Test excluding pattern
        reader = FileSystemReader(tmp_path, exclude=["test_*.py"])
        files = [f.name for f in reader]
        assert "test_file1.py" not in files
        assert "test_file2.py" not in files
        assert "keep_file.txt" in files


def test_filesystem_reader_with_exclude_and_extensions():
    """Test FileSystemReader with exclude parameter and extensions filtering."""
    import os

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        # Create test files
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / "exclude_me.txt").touch()
        (tmp_path / "keep_me.md").touch()
        # Create subdirectory with files
        sub_dir = tmp_path / "subdir"
        sub_dir.mkdir()
        (sub_dir / "sub_file.txt").touch()
        (sub_dir / "sub_file.py").touch()
        # Test excluding specific file and filtering by extensions
        reader = FileSystemReader(
            [tmp_path],
            extensions=[".txt", ".md"],
            exclude=["exclude_me.txt", sub_dir / "sub_file.txt"],
        )
        files = [f.name for f in reader]
        assert "exclude_me.txt" not in files
        assert "file1.txt" in files
        assert "file2.py" not in files  # .py not in extensions
        assert "keep_me.md" in files
        assert "sub_file.txt" not in files  # excluded
        assert "sub_file.py" not in files  # .py not in extensions
