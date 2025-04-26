# Pushlog Tests

This directory contains tests for the pushlog daemon. The tests cover the various components and functionality of the application.

## Test Structure

- `test_config.py`: Tests for configuration loading and parsing
- `test_pattern_matching.py`: Tests for unit matching, pattern matching, and fuzzy deduplication
- `test_notifications.py`: Tests for message formatting and sending notifications
- `test_history.py`: Tests for history buffer management and cleanup
- `test_daemon.py`: Tests for the main daemon functionality with mocked components

## Running the Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_config.py
```

To run a specific test case:

```bash
pytest tests/test_config.py::TestConfig::test_load_config
```

To run with coverage:

```bash
pytest --cov=pushlog_lib
```

## Installing Test Dependencies

You can install the test dependencies with:

```bash
pip install -e ".[dev]"
```

## Test Configuration

The test configuration file (`fixtures/test_config.yaml`) contains a sample configuration for testing, including various units, patterns, and priority mappings.

## Mocking

The tests use Python's `unittest.mock` module to mock external dependencies such as:

- `systemd.journal.Reader` for journal access
- `HTTPSConnection` for Pushover API calls
- `datetime` for time-based tests

This allows the tests to run without requiring actual system journal access or making actual API calls.
