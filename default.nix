{
  lib,
  python3Packages,
}:
python3Packages.buildPythonApplication rec {
  pname = "pushlog";
  version = "0.2.0";

  src = ./.;

  propagatedBuildInputs = with python3Packages; [
    click
    fuzzywuzzy
    pyyaml
    systemd
  ];

  # checkInputs = with python3Packages; [
  #   pytestCheckHook
  # ];

  meta = with lib; {
    description = "Pushlog journal forwarder";
    longDescription = ''
      A lightweight Python daemon that filters and forwards journald log messages to Pushover
    '';
    homepage = "https://github.com/serpent213/pushlog";
    platforms = platforms.linux;
    mainProgram = "pushlog";
    license = licenses.bsd0;
    # maintainers = with maintainers; [ ];
  };
}
