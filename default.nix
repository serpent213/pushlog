{ lib, python3Packages }:

python3Packages.buildPythonApplication rec {
  pname = "pushlog";
  version = "0.1.0";

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
    license = licenses.bsd0;
    # maintainers = with maintainers; [ ];
  };
}
