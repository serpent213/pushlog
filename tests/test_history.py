#!/usr/bin/env python3

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from pushlog_lib import cleanup_history


class TestHistoryCleanup(unittest.TestCase):
    def setUp(self):
        # Create a history buffer with entries of various ages
        self.now = datetime.now()
        self.history = {
            "recent_message": self.now - timedelta(minutes=5),  # 5 minutes old
            "old_message": self.now - timedelta(minutes=40),  # 40 minutes old
            "very_old_message": self.now - timedelta(hours=2),  # 2 hours old
        }

    @patch("pushlog_lib.datetime")
    def test_cleanup_history(self, mock_datetime):
        """Test cleaning up old entries from the history buffer."""
        # Mock the datetime.now() call to return a fixed time
        mock_datetime.now.return_value = self.now

        # Set the deduplication window to 30 minutes
        deduplication_window = 30

        # Call the cleanup function
        cleanup_history(self.history, deduplication_window)

        # Check that only recent messages remain
        self.assertIn("recent_message", self.history)
        self.assertNotIn("old_message", self.history)
        self.assertNotIn("very_old_message", self.history)

        # Check that we have only one message left
        self.assertEqual(len(self.history), 1)

    @patch("pushlog_lib.datetime")
    def test_cleanup_history_larger_window(self, mock_datetime):
        """Test cleaning up with a larger deduplication window."""
        # Mock the datetime.now() call to return a fixed time
        mock_datetime.now.return_value = self.now

        # Set the deduplication window to 60 minutes
        deduplication_window = 60

        # Call the cleanup function
        cleanup_history(self.history, deduplication_window)

        # Check that recent and moderately old messages remain
        self.assertIn("recent_message", self.history)
        self.assertIn("old_message", self.history)
        self.assertNotIn("very_old_message", self.history)

        # Check that we have two messages left
        self.assertEqual(len(self.history), 2)

    @patch("pushlog_lib.datetime")
    def test_cleanup_history_empty(self, mock_datetime):
        """Test cleaning up an empty history buffer."""
        # Mock the datetime.now() call to return a fixed time
        mock_datetime.now.return_value = self.now

        # Create an empty history buffer
        empty_history = {}

        # Set the deduplication window to 30 minutes
        deduplication_window = 30

        # Call the cleanup function
        cleanup_history(empty_history, deduplication_window)

        # Check that the history is still empty
        self.assertEqual(len(empty_history), 0)


if __name__ == "__main__":
    unittest.main()
