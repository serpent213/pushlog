#!/usr/bin/env python3

import os
import unittest
from unittest.mock import patch

import pytest
import yaml

from pushlog_lib import load_config


class TestConfig(unittest.TestCase):
    def setUp(self):
        # Path to the test config file
        self.config_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "test_config.yaml"
        )

    def test_load_config(self):
        """Test loading and parsing the configuration file."""
        config = load_config(self.config_path)

        # Check basic configuration values
        self.assertEqual(config["collect_timeout"], 5)
        self.assertEqual(config["deduplication_window"], 30)
        self.assertEqual(config["fuzzy_threshold"], 95)
        self.assertEqual(config["title"], "Test Logs")

        # Check pushover configuration
        self.assertEqual(config["pushover"]["token"], "test_token")
        self.assertEqual(config["pushover"]["user"], "test_user")

        # Check priority mapping
        self.assertEqual(config["priority_map"]["0"], 2)
        self.assertEqual(config["priority_map"]["3"], 0)
        self.assertEqual(config["priority_map"]["7"], -2)

        # Check units configuration
        self.assertEqual(len(config["units"]), 3)

        # Check first unit
        unit = config["units"][0]
        self.assertEqual(unit.priorities, [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(len(unit.include_regexs), 0)
        self.assertEqual(len(unit.exclude_regexs), 1)

        # Check second unit
        unit = config["units"][1]
        self.assertEqual(unit.priorities, [0, 1, 2, 3])
        self.assertEqual(len(unit.include_regexs), 2)
        self.assertEqual(len(unit.exclude_regexs), 1)

        # Check third unit with regex pattern
        unit = config["units"][2]
        self.assertEqual(len(unit.include_regexs), 1)
        self.assertEqual(len(unit.exclude_regexs), 0)

    @patch("builtins.open")
    def test_load_config_file_not_found(self, mock_open):
        """Test behavior when the config file is not found."""
        mock_open.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")

    @patch("yaml.safe_load")
    def test_load_config_invalid_yaml(self, mock_yaml_load):
        """Test behavior with invalid YAML."""
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")

        with self.assertRaises(yaml.YAMLError):
            load_config(self.config_path)


if __name__ == "__main__":
    unittest.main()
