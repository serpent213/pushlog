# Pushlog

A lightweight Python daemon that filters and forwards journald log messages to [Pushover](https://pushover.net/).

Depends on [python-systemd](https://github.com/systemd/python-systemd), so it typically will only
run on Linux systems.

## Features

- Filter messages by systemd unit name with regex patterns
- Filter messages by priority levels
- Include/exclude messages based on content patterns
- Deduplication with fuzzy matching to avoid notification spam
- Configurable notification batching with timeout window
- Map journald priorities to Pushover priorities

## Installation

### Standalone

1. Clone this repository
2. Install dependencies: `python3 -m pip install -r requirements.txt`
3. Copy `config.yaml` to a suitable location and edit it
4. Run: `./pushlog --config /path/to/config.yaml`

You will need to set your Pushover API token and user key either in the config file or via
environment variables:

```bash
export PUSHLOG_PUSHOVER_TOKEN="your-app-token"
export PUSHLOG_PUSHOVER_USER_KEY="your-user-key" 
```

### NixOS Module

To include the module into your NixOS configuration:

```nix
imports = [
  ((builtins.fetchTarball {
    url = "https://github.com/serpent213/pushlog/archive/v0.1.0.tar.gz";
    sha256 = "sha256:18jihyg5dqysm412chi4dfacfyrifr48cgf6qrfnsva8rjbw8s1l";
  }) + "/module.nix")
];

services.pushlog = {
  enable = true;
  # Load Pushover credentials from an environment file
  # Contains PUSHLOG_PUSHOVER_TOKEN and PUSHLOG_PUSHOVER_USER_KEY
  environmentFile = "/path/to/pushlog.env";

  settings = {
    # Optional title for all notifications
    title = "System Logs";

    # Optional priority mapping
    priority-map = {
      "0" = 2;  # emerg -> emergency (2)
      "1" = 1;  # alert -> high (1)
      "2" = 1;  # crit -> high (1)
    };

    # Units to monitor (first match wins)
    units = [
      {
        match = "node-red";
        priorities = [ 0 1 2 3 4 5 6 ];
        include = [];
        exclude = [ "[{}]" ];
      }
      {
        match = ".*";
        priorities = [ 0 1 2 3 4 5 6 ];
        include = [ "error" "warning" "critical" ];
        exclude = [];
      }
    ];
  };
};
```

If using agenix for secrets, you can use:

```nix
services.pushlog = {
  enable = true;
  environmentFile = config.age.secrets."pushlog.env".path;
  # ... rest of configuration
};
```

## Configuration

See the commented `config.yaml` file for a complete example of all available options.

### Key Configuration Options

- `collect-timeout`: Seconds to wait before sending collected messages (default: 5)
- `deduplication-window`: Minutes to remember messages to avoid duplicates (default: 30)
- `fuzzy-threshold`: Similarity percentage for fuzzy deduplication (default: 95, set 100 to disable)
- `title`: Optional title for all Pushover notifications
- `priority-map`: Optional mapping from journald to Pushover priorities

### Unit Configuration

Each unit entry in the `units` list supports:

- `match`: Regex pattern to match against the systemd unit name
- `priorities`: List of journald priorities to include (0-7)
- `include`: List of regex patterns to match in message content (empty matches all)
- `exclude`: List of regex patterns to exclude from matches

Journald priorities:

- 0: emerg
- 1: alert
- 2: crit
- 3: err
- 4: warning
- 5: notice
- 6: info
- 7: debug

Pushover priorities:

- -2: lowest
- -1: low
- 0: normal (default)
- 1: high
- 2: emergency
