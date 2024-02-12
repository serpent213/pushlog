# Pushlog

Follows *journald* and forwards selected messages to Pushover.

To include the module into your NixOS configuration (using *agenix*):

```nix
imports = [
  ((builtins.fetchTarball {
    url = "https://github.com/serpent213/pushlog/archive/v0.1.0.tar.gz";
    sha256 = "sha256:18jihyg5dqysm412chi4dfacfyrifr48cgf6qrfnsva8rjbw8s1l";
  }) + "/module.nix")
];

services.pushlog = {
  enable = true;
  environmentFile = config.age.secrets."pushlog.env".path;
  settings.units = [
    {
      match = ".*";
    }
  ];
};
```

See `config.yaml` for options.
