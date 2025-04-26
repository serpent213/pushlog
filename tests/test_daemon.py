#!/usr/bin/env python3
"""Tests for the daemon functionality."""

import os
import unittest
from datetime import datetime

from pushlog_lib import load_config, should_process_entry


class TestDaemon(unittest.TestCase):
    """Test cases for the daemon functionality and components."""
    def setUp(self):
        # Path to the test config file
        self.config_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "test_config.yaml"
        )

        # Sample journal entry
        self.journal_entry = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "SYSLOG_IDENTIFIER": "test-process",
            "__REALTIME_TIMESTAMP": datetime.now(),
            "PRIORITY": 3,
            "MESSAGE": "This is a test message",
        }

    def test_daemon_components(self):
        """Test the key components that make up the daemon."""
        # Test that we can load the config successfully
        config = load_config(self.config_path)
        self.assertEqual(config["collect_timeout"], 5)
        self.assertEqual(config["fuzzy_threshold"], 95)

        # Test that units are properly parsed
        units = config["units"]
        self.assertEqual(len(units), 3)
        self.assertEqual(units[0].priorities, [0, 1, 2, 3, 4, 5, 6])

        # Test message processing with the loaded config
        history_buffer = {}
        result = should_process_entry(
            self.journal_entry, units, config["fuzzy_threshold"], history_buffer
        )
        self.assertTrue(result)

        # Test that the message was added to history
        self.assertEqual(len(history_buffer), 1)
        self.assertTrue(self.journal_entry["MESSAGE"] in history_buffer)


if __name__ == "__main__":
    unittest.main()
