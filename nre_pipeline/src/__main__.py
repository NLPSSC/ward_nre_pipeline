#!/usr/bin/env python3
"""
CLI entry point for the NRE Pipeline project.
"""

import sys
import argparse
from nre_pipeline import main


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Non-Routine Events (NRE) Pipeline",
        prog="nre_pipeline"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Add more arguments as needed
    
    return parser


def cli_main():
    """Main CLI function."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Call the main function from the nre_pipeline module
        return main.run(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(cli_main())
