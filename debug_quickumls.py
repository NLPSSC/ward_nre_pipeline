#!/usr/bin/env python3
"""
Debug script for testing QuickUMLS setup and functionality.
"""

import os
from pathlib import Path

from quickumls import QuickUMLS


def test_quickumls():
    """Test QuickUMLS installation and basic functionality."""

    # Get QuickUMLS path
    quickumls_path = os.getenv("QUICKUMLS_PATH", "./quickumls")
    print(f"QuickUMLS path: {quickumls_path}")

    # Check if path exists
    path_obj = Path(quickumls_path)
    if not path_obj.exists():
        print(f"ERROR: QuickUMLS path does not exist: {quickumls_path}")
        return False

    # Check required files
    required_files = [
        "database_backend.flag",
        "language.flag",
        "cui-semtypes.db",
        "umls-simstring.db",
    ]
    print("\nChecking required files:")
    for required_file in required_files:
        file_path = path_obj / required_file
        exists = file_path.exists()
        print(f"  {required_file}: {'✓' if exists else '✗'}")
        if not exists:
            print(f"    Missing: {file_path}")

    # Try to initialize QuickUMLS
    print("\nInitializing QuickUMLS...")
    try:
        matcher = QuickUMLS(path_obj)
        print("✓ QuickUMLS initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize QuickUMLS: {e}")
        return False

    # Test with sample medical texts
    test_texts = [
        "diabetes mellitus",
        "hypertension",
        "myocardial infarction",
        "pneumonia",
        "The patient has diabetes and high blood pressure.",
        "Patient presents with chest pain and shortness of breath.",
        "Diagnosis: acute myocardial infarction",
    ]

    print("\nTesting with sample medical texts:")
    total_matches = 0

    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: '{text}'")
        try:
            matches = matcher.match(text)
            match_count = sum(len(group) for group in matches)
            total_matches += match_count
            print(f"  Found {match_count} matches in {len(matches)} groups")

            # Show first few matches for debugging
            shown = 0
            for group in matches:
                for match in group:
                    if shown < 3:  # Show max 3 matches per text
                        print(
                            f"    - {match['term']} (CUI: {match['cui']}, sim: {match['similarity']:.3f})"
                        )
                        shown += 1
                    else:
                        break
                if shown >= 3:
                    break

        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nTotal matches found across all tests: {total_matches}")

    if total_matches == 0:
        print("\n⚠️  WARNING: No matches found! Possible issues:")
        print("1. QuickUMLS database may be empty or corrupted")
        print("2. Database may not contain the expected medical terms")
        print("3. Configuration files may be incorrect")
        print("4. QuickUMLS installation may be incomplete")

        # Additional diagnostic info
        print("\nDiagnostic info:")
        try:
            with open(path_obj / "database_backend.flag", "r") as f:
                backend = f.read().strip()
                print(f"  Database backend: {backend}")
        except Exception as e:
            print(f"  Could not read database backend: {e}")

        try:
            with open(path_obj / "language.flag", "r") as f:
                language = f.read().strip()
                print(f"  Language: {language}")
        except Exception as e:
            print(f"  Could not read language: {e}")
    else:
        print("\n✓ QuickUMLS appears to be working correctly!")

    return total_matches > 0


if __name__ == "__main__":
    print("QuickUMLS Debug Script")
    print("=" * 50)

    success = test_quickumls()

    print("\n" + "=" * 50)
    if success:
        print("✓ QuickUMLS test completed successfully")
    else:
        print("✗ QuickUMLS test failed - check the issues above")
