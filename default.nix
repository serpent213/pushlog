{
  lib ? (import <nixpkgs> {}).lib,
  python3Packages ? (import <nixpkgs> {}).python3Packages,
}:
python3Packages.buildPythonApplication {
  pname = "pushlog";
  version = "0.3.0";
  format = "pyproject";

  src = ./.;

  propagatedBuildInputs = with python3Packages; [
    click
    fuzzywuzzy
    levenshtein
    pyyaml
    setuptools
    systemd
  ];

  checkInputs = with python3Packages; [
    pytestCheckHook
  ];

  meta = with lib; {
    description = "Pushlog systemd journal forwarder";
    longDescription = ''
      A lightweight Python daemon that filters and forwards journald log messages to Pushover
    '';
    homepage = "https://github.com/serpent213/pushlog";
    platforms = platforms.linux;
    mainProgram = "pushlog";
    license = licenses.bsd0;
    maintainers = with maintainers; [serpent213];
  };
}
