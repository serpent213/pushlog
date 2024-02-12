{ lib, config, pkgs, ... }:

with lib;

let
  cfg = config.services.pushlog;
  unitType = types.submodule {
    options = {
      match = mkOption {
        type = types.str;
        default = ".*";
      };
      priorities = mkOption {
        type = types.listOf types.int;
        default = [ 0 1 2 3 4 5 6 ];
      };
      include = mkOption {
        type = types.listOf types.str;
        default = [];
      };
      exclude = mkOption {
        type = types.listOf types.str;
        default = [];
      };
    };
  };
in
{
  options.services.pushlog = {
    enable = mkEnableOption "Enable pushlog service to forward journald logs to Pushover";

    package = mkOption {
      type = types.package;
      description = "pushlog package to use";
      default = (pkgs.callPackage ./default.nix {});
      defaultText = "./pushlog.nix";
    };

    environmentFile = mkOption {
      type = with types; nullOr str;
      description = lib.mdDoc ''
        File containing the Pushover API credentials, in the
        format of an EnvironmentFile as described by systemd.exec(5)

        PUSHLOG_PUSHOVER_TOKEN, PUSHLOG_PUSHOVER_USER_KEY
      '';
      default = null;
    };

    settings = {
      collect-timeout = mkOption {
        type = types.int;
        description = "Wait n seconds before sendings logs to bundle multiple messages";
        default = 5;
      };
      deduplication-window = mkOption {
        type = types.int;
        description = "Remember messages for n minutes and avoid sending duplicates";
        default = 30;
      };
      fuzzy-threshold = mkOption {
        type = types.int;
        description = "Use fuzzy matching with the given threshold (similarity in percent) to detect duplicates, set to 100 to disable";
        default = 95;
      };
      units = mkOption {
        type = types.listOf unitType;
        description = "List of units to care about";
      };
    };
  };

  config = mkIf cfg.enable
    (let
      format = pkgs.formats.yaml { };
      configFile = format.generate "pushlog.yaml" cfg.settings;
    in
    {
      systemd.services.pushlog = {
        description = "Pushlog journal forwarder";
        after = [ "network-online.target" "systemd-journald.service" ];
        wants = [ "network-online.target" "systemd-journald.service" ];
        wantedBy = [ "multi-user.target" ];
        serviceConfig = {
          ExecStart = "${cfg.package}/bin/pushlog --config ${configFile}";
          Type = "simple";
          Restart = "always";
          RestartSec = "5s";
          NoNewPrivileges = true;
          PrivateTmp = true;
          PrivateDevices = true;
          ProtectHome = true;
          ProtectSystem = "full";
        } // optionalAttrs (cfg.environmentFile != null) {
          EnvironmentFile = cfg.environmentFile;
        };
      };
    });
}
