#!/usr/bin/env python3

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from pushlog_lib import (format_message, send_collected_messages,
                         send_pushover_notification)


class TestNotifications(unittest.TestCase):
    def setUp(self):
        # Sample journal entry
        self.entry = {
            "_SYSTEMD_UNIT": "test-unit.service",
            "SYSLOG_IDENTIFIER": "test-process",
            "__REALTIME_TIMESTAMP": datetime.now(),
            "PRIORITY": 3,
            "MESSAGE": "This is a test message",
        }

        # Sample pushover config
        self.pushover_config = {
            "token": "test_token",
            "user": "test_user",
            "title": "Test Logs",
            "priority_map": {
                "0": 2,  # emerg -> emergency
                "1": 1,  # alert -> high
                "2": 1,  # crit -> high
                "3": 0,  # err -> normal
                "4": -1,  # warning -> low
                "5": -2,  # notice -> lowest
                "6": -2,  # info -> lowest
                "7": -2,  # debug -> lowest
            },
        }

    def test_format_message(self):
        """Test formatting a journal entry for display."""
        formatted = format_message(self.entry)

        # Check that the formatted message contains all the key components
        self.assertIn(str(self.entry["__REALTIME_TIMESTAMP"]), formatted)
        self.assertIn(self.entry["_SYSTEMD_UNIT"], formatted)
        self.assertIn(self.entry["SYSLOG_IDENTIFIER"], formatted)
        self.assertIn(self.entry["MESSAGE"], formatted)

    @patch("pushlog_lib.send_pushover_notification")
    def test_send_collected_messages(self, mock_send_notification):
        """Test sending collected messages."""
        entries = [self.entry]

        # Call the function
        send_collected_messages(entries, self.pushover_config)

        # Check that send_pushover_notification was called with the right parameters
        mock_send_notification.assert_called_once()
        args, kwargs = mock_send_notification.call_args

        # Check that the message contains our test message
        self.assertIn(self.entry["MESSAGE"], args[0])

        # Check that the config was passed correctly
        self.assertEqual(args[1], self.pushover_config)

        # Check that the priority was passed correctly
        self.assertEqual(args[2], 3)

    @patch("pushlog_lib.send_pushover_notification")
    def test_send_collected_messages_custom_sender(self, mock_default_sender):
        """Test sending collected messages with a custom notification sender."""
        entries = [self.entry]

        # Create a mock custom sender
        mock_custom_sender = MagicMock()

        # Call the function with the custom sender
        send_collected_messages(entries, self.pushover_config, mock_custom_sender)

        # Check that the default sender was not called
        mock_default_sender.assert_not_called()

        # Check that our custom sender was called with the right parameters
        mock_custom_sender.assert_called_once()
        args, kwargs = mock_custom_sender.call_args

        # Check that the message contains our test message
        self.assertIn(self.entry["MESSAGE"], args[0])

        # Check that the config was passed correctly
        self.assertEqual(args[1], self.pushover_config)

        # Check that the priority was passed correctly
        self.assertEqual(args[2], 3)

    @patch("http.client.HTTPSConnection")
    def test_send_pushover_notification(self, mock_https_connection):
        """Test sending a notification to Pushover."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_connection = MagicMock()
        mock_connection.getresponse.return_value = mock_response
        mock_https_connection.return_value = mock_connection

        # Call the function
        send_pushover_notification("Test message", self.pushover_config, 3)

        # Check that the connection was created correctly
        mock_https_connection.assert_called_once_with("api.pushover.net:443")

        # Check that the request was made correctly
        mock_connection.request.assert_called_once()
        args, kwargs = mock_connection.request.call_args

        # Check the request method and URL
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "/1/messages.json")

        # Check that the request body contains the expected parameters
        self.assertIn("token=test_token", args[2])
        self.assertIn("user=test_user", args[2])
        self.assertIn("message=Test+message", args[2])
        self.assertIn("title=Test+Logs", args[2])
        self.assertIn("priority=0", args[2])  # Priority 3 maps to 0

    @patch("http.client.HTTPSConnection")
    def test_send_pushover_notification_error(self, mock_https_connection):
        """Test error handling when sending a notification to Pushover."""
        # Setup mock response with error status
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.reason = "Bad Request"
        mock_connection = MagicMock()
        mock_connection.getresponse.return_value = mock_response
        mock_https_connection.return_value = mock_connection

        # Call the function (should not raise an exception)
        with patch("sys.stderr") as mock_stderr:
            send_pushover_notification("Test message", self.pushover_config, 3)

        # Check that the error was reported
        mock_stderr.write.assert_called()

    @patch("http.client.HTTPSConnection")
    def test_send_pushover_notification_exception(self, mock_https_connection):
        """Test exception handling when sending a notification to Pushover."""
        # Setup mock to raise an exception
        mock_https_connection.side_effect = Exception("Connection error")

        # Call the function (should not raise an exception)
        with patch("sys.stderr") as mock_stderr:
            send_pushover_notification("Test message", self.pushover_config, 3)

        # Check that the error was reported
        mock_stderr.write.assert_called()


if __name__ == "__main__":
    unittest.main()
