{
  lib ? (import <nixpkgs> {}).lib,
  python3Packages ? (import <nixpkgs> {}).python3Packages,
}:
python3Packages.buildPythonApplication {
  pname = "pushlog";
  version = "0.3.1";
  format = "pyproject";

  src = ./.;

  nativeBuildInputs = with python3Packages; [
    setuptools
  ];

  propagatedBuildInputs = with python3Packages; [
    click
    fuzzywuzzy
    levenshtein
    pyyaml
    systemd
  ];

  checkInputs = with python3Packages; [
    pytestCheckHook
  ];

  meta = {
    description = "Pushlog systemd journal forwarder";
    longDescription = ''
      A lightweight Python daemon that filters and forwards journald log messages to Pushover
    '';
    homepage = "https://github.com/serpent213/pushlog";
    platforms = lib.platforms.linux;
    mainProgram = "pushlog";
    license = lib.licenses.bsd0;
    maintainers = with lib.maintainers; [serpent213];
  };
}
