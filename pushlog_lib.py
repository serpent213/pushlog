#!/usr/bin/env python3

import http.client
import os
import re
import sys
import urllib
from collections import namedtuple
from datetime import datetime, timedelta

import click
import systemd.journal
import yaml
from fuzzywuzzy import process

Unit = namedtuple("Unit", ["match", "priorities", "include_regexs", "exclude_regexs"])


def load_config(config_path):
    """Load and parse the YAML configuration file."""
    with open(config_path, "r") as yaml_file:
        config = yaml.safe_load(yaml_file)
        units = []
        # Pre-compile regular expressions for better performance
        for u in config.get("units", []):
            include_regexs = [re.compile(regex) for regex in u["include"]]
            exclude_regexs = [re.compile(regex) for regex in u["exclude"]]
            units.append(
                Unit(
                    re.compile(u["match"]),
                    u["priorities"],
                    include_regexs,
                    exclude_regexs,
                )
            )

        collect_timeout = config.get("collect-timeout", 5)  # [s]
        deduplication_window = config.get("deduplication-window", 30)  # [min.]
        fuzzy_threshold = config.get("fuzzy-threshold", 92)  # [%]
        pushover = config.get("pushover", {})
        title = config.get("title")
        priority_map = config.get("priority-map", {})
        
    return {
        "units": units, 
        "collect_timeout": collect_timeout,
        "deduplication_window": deduplication_window,
        "fuzzy_threshold": fuzzy_threshold,
        "pushover": pushover,
        "title": title,
        "priority_map": priority_map
    }


def should_process_entry(entry, config_units, fuzzy_threshold, history_buffer):
    """
    Determine if an entry should be processed based on configuration rules.
    Returns True if the entry should be processed, False otherwise.
    """
    # match the _SYSTEMD_UNIT against units' match fields
    unit = next(
        (u for u in config_units if u.match.search(entry.get("_SYSTEMD_UNIT", ""))),
        None,
    )
    if not unit:
        return False

    if not "PRIORITY" in entry or not entry["PRIORITY"] in unit.priorities:
        return False

    message = entry.get("MESSAGE", "")
    if any(regex.search(message) for regex in unit.exclude_regexs):
        return False
    if len(unit.include_regexs) > 0:
        # Pass all messages if no include filter is specified
        if not any(regex.search(message) for regex in unit.include_regexs):
            return False

    if fuzzy_threshold < 100:
        # Check against history buffer (fuzzy match), strip numbers first
        if getattr(should_process_entry, "translation_table", None) is None:
            # use the function object for a hacky singleton
            should_process_entry.translation_table = str.maketrans("", "", "0123456789")
        stripped = message.translate(should_process_entry.translation_table)

        matches = process.extract(stripped, list(history_buffer.keys()), limit=1)
        if (
            len(matches) > 0 and matches[0][1] >= fuzzy_threshold
        ):  # fuzzy matching threshold in %
            return False

    # Pass
    history_buffer[message] = datetime.now()
    return True


def format_message(message):
    """Format a journal entry for display in a notification."""
    unit_name = message.get("_SYSTEMD_UNIT", "")
    syslog_identifier = message.get("SYSLOG_IDENTIFIER", "")
    timestamp = message.get("__REALTIME_TIMESTAMP")
    message_text = message.get("MESSAGE", "")

    result = f"{timestamp} {unit_name}[{syslog_identifier}]: {message_text}"

    return result


def send_collected_messages(entries_buffer, pushover, notification_sender=None):
    """Format and send a collection of messages as a notification."""
    if entries_buffer:
        formatted_messages = [format_message(msg) for msg in entries_buffer]
        full_text = "\n".join(formatted_messages)

        # Determine the highest priority message in the batch
        highest_priority = None
        for entry in entries_buffer:
            if "PRIORITY" in entry:
                entry_priority = int(entry["PRIORITY"])
                if highest_priority is None or entry_priority < highest_priority:
                    highest_priority = entry_priority

        if notification_sender:
            notification_sender(full_text, pushover, highest_priority)
        else:
            send_pushover_notification(full_text, pushover, highest_priority)


def send_pushover_notification(message, pushover, journald_priority=None):
    """Send a notification to Pushover."""
    params = {
        "token": pushover.get("token"),
        "user": pushover.get("user"),
        "message": message,
    }

    if "title" in pushover:
        params["title"] = pushover.get("title")

    # Map journald priority to Pushover priority if mapping exists
    if (
        journald_priority is not None
        and "priority_map" in pushover
        and str(journald_priority) in pushover["priority_map"]
    ):
        params["priority"] = pushover["priority_map"][str(journald_priority)]

    try:
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request(
            "POST",
            "/1/messages.json",
            urllib.parse.urlencode(params),
            {"Content-type": "application/x-www-form-urlencoded"},
        )
        response = conn.getresponse()
        if response.status != 200:
            print(
                f"Pushover API error: {response.status} {response.reason}",
                file=sys.stderr,
            )
    except Exception as e:
        print(f"Error sending notification to Pushover: {e}", file=sys.stderr)


def cleanup_history(history_buffer, deduplication_window):
    """Remove old entries from the history buffer."""
    for message in list(history_buffer):
        if datetime.now() - history_buffer[message] > timedelta(
            minutes=deduplication_window
        ):
            del history_buffer[message]


def run_daemon(config_path, journal_reader=None, notification_sender=None):
    """Run the main daemon loop."""
    config_data = load_config(config_path)
    units = config_data["units"]
    collect_timeout = config_data["collect_timeout"]
    deduplication_window = config_data["deduplication_window"]
    fuzzy_threshold = config_data["fuzzy_threshold"]
    pushover = config_data["pushover"]
    title = config_data["title"]
    priority_map = config_data["priority_map"]
    cleanup_interval = 60  # [s]

    if "PUSHLOG_PUSHOVER_TOKEN" in os.environ:
        pushover["token"] = os.environ["PUSHLOG_PUSHOVER_TOKEN"]
    if "PUSHLOG_PUSHOVER_USER_KEY" in os.environ:
        pushover["user"] = os.environ["PUSHLOG_PUSHOVER_USER_KEY"]
    if title:
        pushover["title"] = title
    if priority_map:
        pushover["priority_map"] = priority_map
    if not pushover.get("token") or not pushover.get("user"):
        print(f"Pushover API credentials missing. Aborting.", file=sys.stderr)
        sys.exit(1)

    if journal_reader is None:
        j = systemd.journal.Reader()
        j.log_level(systemd.journal.LOG_INFO)
        j.this_boot()
        j.seek_tail()
        j.get_previous()
    else:
        j = journal_reader

    entries_buffer = []
    history_buffer = {}
    last_entry_time = datetime.now()
    last_cleanup_time = datetime.now()
    collection_triggered = False
    while True:
        if j.wait(1) == systemd.journal.APPEND:
            for entry in j:
                if should_process_entry(entry, units, fuzzy_threshold, history_buffer):
                    entries_buffer.append(entry)
                    if not collection_triggered:
                        last_entry_time = datetime.now()
                        collection_triggered = True

        if (
            collection_triggered
            and (datetime.now() - last_entry_time).total_seconds() >= collect_timeout
        ):
            send_collected_messages(entries_buffer, pushover, notification_sender)
            entries_buffer = []
            collection_triggered = False

        if (datetime.now() - last_cleanup_time).total_seconds() >= cleanup_interval:
            cleanup_history(history_buffer, deduplication_window)
            last_cleanup_time = datetime.now()


@click.command()
@click.option(
    "--config",
    prompt="Path to configuration file",
    help="The YAML configuration file to apply.",
)
def main(config):
    run_daemon(config)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])