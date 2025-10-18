"""
Test module for the NRE Pipeline.

This module contains unit tests for the main functionality.
"""

import unittest
from nre_pipeline import main


class TestNREPipeline(unittest.TestCase):
    """Test cases for the NRE Pipeline main module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_data = {
            "events": [
                {"id": 1, "type": "incident", "description": "Test event 1"},
                {"id": 2, "type": "alert", "description": "Test event 2"}
            ]
        }
    
    def test_process_events_with_data(self):
        """Test processing events with valid data."""
        result = main.process_events(self.sample_data)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "processed")
        self.assertEqual(result["events_count"], 2)
        self.assertIn("results", result)
    
    def test_process_events_empty_data(self):
        """Test processing events with empty data."""
        empty_data = {"events": []}
        result = main.process_events(empty_data)
        
        self.assertEqual(result["events_count"], 0)
        self.assertEqual(result["status"], "processed")
    
    def test_process_events_no_events_key(self):
        """Test processing events when events key is missing."""
        no_events_data = {"other_data": "test"}
        result = main.process_events(no_events_data)
        
        self.assertEqual(result["events_count"], 0)


class TestMainArguments(unittest.TestCase):
    """Test cases for command line argument handling."""
    
    def test_setup_logging_verbose(self):
        """Test logging setup with verbose mode."""
        # This is a basic test - in practice you might want to check
        # the actual logging level set
        try:
            main.setup_logging(verbose=True)
            # If no exception is raised, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"setup_logging raised an exception: {e}")
    
    def test_setup_logging_normal(self):
        """Test logging setup with normal mode."""
        try:
            main.setup_logging(verbose=False)
            # If no exception is raised, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"setup_logging raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
