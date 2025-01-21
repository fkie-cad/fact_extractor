#!/usr/bin/env bash
set -euxo pipefail

echo "Install Pre-Install Requirements"
(apt-get update && apt-get install -y sudo) || true

sudo apt-get update
sudo apt-get install -y git apt-transport-https ca-certificates curl software-properties-common wget libmagic-dev xz-utils

IS_VENV=$(python3 -c 'import sys; print(sys.exec_prefix!=sys.base_prefix)')
if [[ $IS_VENV == "False" ]]
then
  SUDO="sudo -EH"
  sudo apt-get install -y python3-pip python3-wheel python3-setuptools
else
  SUDO=""
fi

$SUDO pip3 install --upgrade pip setuptools wheel "packaging>=22"
$SUDO pip3 install --upgrade distro
$SUDO pip3 install --upgrade git+https://github.com/fkie-cad/common_helper_files.git
$SUDO pip3 install --upgrade git+https://github.com/fkie-cad/common_helper_process.git

exit 0
