# Pushlog

Follows *journald* and forwards selected messages to Pushover.

To include the module into your NixOS configuration (using *agenix*):

```nix
imports = [
  ((builtins.fetchTarball {
    url = "https://github.com/serpent213/pushlog/archive/fb56c828e59bba140718d81acc53942fffc9b4e7.tar.gz";
    sha256 = "sha256:112ml0fkdvzvpfin47lfacn6b4b97idmn78gkp1q1gmavn370asp";
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
