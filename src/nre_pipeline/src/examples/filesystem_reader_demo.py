"""
Example usage of FileSystemReader class.
"""

from pathlib import Path

from nre_pipeline.reader import FileSystemReader


def main():
    """Demonstrate FileSystemReader usage."""
    # Example 1: Basic iteration over all files
    print("Example 1: Iterating over all files in current directory")
    current_dir = Path.cwd()
    reader = FileSystemReader(current_dir)

    file_count = 0
    for file_path in reader:
        print(f"  {file_path}")
        file_count += 1
        if file_count >= 10:  # Limit output for demo
            print("  ... (truncated)")
            break

  

    # Example 4: Count files by extension
    print("\nExample 4: File count by extension")
    extensions = {}
    for file_path in reader:
        ext = file_path.suffix.lower() or "no_extension"
        extensions[ext] = extensions.get(ext, 0) + 1

    for ext, count in sorted(extensions.items()):
        print(f"  {ext}: {count} files")


if __name__ == "__main__":
    main()
