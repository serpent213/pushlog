#!/usr/bin/env python3
"""Tests for the pattern matching functionality."""

import re
import unittest

from pushlog_lib import Unit, should_process_entry


class TestPatternMatching(unittest.TestCase):
    """Test cases for the pattern matching and message processing functionality."""
    def setUp(self):
        # Create test units similar to those in the config
        self.units = [
            Unit(
                match=re.compile("test-unit"),
                priorities=[0, 1, 2, 3, 4, 5, 6],
                include_regexs=[],
                exclude_regexs=[re.compile("exclude_me")],
            ),
            Unit(
                match=re.compile("another-unit"),
                priorities=[0, 1, 2, 3],
                include_regexs=[re.compile("error"), re.compile("critical")],
                exclude_regexs=[re.compile("ignore")],
            ),
            Unit(
                match=re.compile("regex-unit"),
                priorities=[0, 1, 2, 3, 4, 5],
                include_regexs=[re.compile(r"pattern\d+")],
                exclude_regexs=[],
            ),
        ]

        # Create an empty history buffer for testing
        self.history = {}

        # Set fuzzy matching threshold
        self.fuzzy_threshold = 95

    def test_unit_matching(self):
        """Test matching log entries to specific units."""
        # Entry that should match the first unit
        entry = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "This is a test message",
        }

        self.assertTrue(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

        # Entry that should match the second unit
        entry = {
            "_SYSTEMD_UNIT": "another-unit.service",
            "PRIORITY": 2,
            "MESSAGE": "This is a critical error",
        }

        self.assertTrue(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

        # Entry that should not match any unit
        entry = {
            "_SYSTEMD_UNIT": "unknown-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "This is a test message",
        }

        self.assertFalse(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

    def test_priority_matching(self):
        """Test matching log entries by priority."""
        # Entry with priority that should match
        entry = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "This is a test message",
        }

        self.assertTrue(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

        # Entry with priority that should not match
        entry = {
            "_SYSTEMD_UNIT": "another-unit.service",
            "PRIORITY": 6,  # Not in the priorities list for the second unit
            "MESSAGE": "This is a critical error",
        }

        self.assertFalse(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

        # Entry without priority field
        entry = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "MESSAGE": "This is a test message",
        }

        self.assertFalse(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

    def test_include_exclude_patterns(self):
        """Test include and exclude pattern matching."""
        # Entry that should match the include pattern
        entry = {
            "_SYSTEMD_UNIT": "another-unit.service",
            "PRIORITY": 2,
            "MESSAGE": "This is a critical error",
        }

        self.assertTrue(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

        # Entry that should not match include pattern
        entry = {
            "_SYSTEMD_UNIT": "another-unit.service",
            "PRIORITY": 2,
            "MESSAGE": "This is a warning message",  # Doesn't match include pattern
        }

        self.assertFalse(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

        # Entry that matches exclude pattern
        entry = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "This message should exclude_me",
        }

        self.assertFalse(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

    def test_regex_pattern_matching(self):
        """Test regex pattern matching."""
        # Entry that should match regex pattern
        entry = {
            "_SYSTEMD_UNIT": "regex-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "This is pattern123 matching",
        }

        self.assertTrue(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

        # Entry that should not match regex pattern
        entry = {
            "_SYSTEMD_UNIT": "regex-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "This is patternXYZ matching",  # Doesn't match pattern\d+
        }

        self.assertFalse(
            should_process_entry(entry, self.units, self.fuzzy_threshold, self.history)
        )

    def test_fuzzy_deduplication(self):
        """Test fuzzy deduplication of similar messages."""
        # First entry
        entry1 = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "Error A12: Connection failed",
        }

        # This should be processed
        self.assertTrue(
            should_process_entry(entry1, self.units, self.fuzzy_threshold, self.history)
        )

        # Similar entry with different ID (should be deduplicated)
        entry2 = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "Error B12: Connection failed",
        }

        # This should be deduplicated due to fuzzy matching
        self.assertFalse(
            should_process_entry(entry2, self.units, self.fuzzy_threshold, self.history)
        )

        # Different message (should be processed)
        entry3 = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "Warning: Disk space low",
        }

        # This should be processed as it's different
        self.assertTrue(
            should_process_entry(entry3, self.units, self.fuzzy_threshold, self.history)
        )

    def test_fuzzy_deduplication_numbers(self):
        """Test fuzzy deduplication number stripping."""
        # First entry
        entry1 = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "2025/04/27 01:53:26.530198+02:00 - Error A12: Connection failed",
        }

        # This should be processed
        self.assertTrue(
            should_process_entry(entry1, self.units, self.fuzzy_threshold, self.history)
        )

        # Similar entry with different timestamp (should be deduplicated)
        entry2 = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "2025/04/27 01:58:26.923006+02:00 - Error A12: Connection failed",
        }

        # This should be deduplicated due to number stripping
        self.assertFalse(
            should_process_entry(entry2, self.units, self.fuzzy_threshold, self.history)
        )

    def test_fuzzy_threshold_disabled(self):
        """Test when fuzzy matching is disabled (threshold=100)."""
        # First entry
        entry1 = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "Error 123: Connection failed",
        }

        # This should be processed
        self.assertTrue(should_process_entry(entry1, self.units, 100, self.history))

        # Similar entry with different numbers (should be processed with threshold=100)
        entry2 = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "PRIORITY": 3,
            "MESSAGE": "Error 456: Connection failed",
        }

        # This should be processed because fuzzy matching is disabled
        self.assertTrue(should_process_entry(entry2, self.units, 100, self.history))


if __name__ == "__main__":
    unittest.main()
