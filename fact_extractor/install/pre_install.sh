#!/usr/bin/env bash

echo "Install Pre-Install Requirements"
(apt-get update && apt-get install sudo) || true

sudo apt-get update
sudo apt-get -y install python3-pip python3-wheel python3-setuptools
sudo apt-get -y install git apt-transport-https ca-certificates curl software-properties-common wget libmagic-dev

sudo -EH pip3 install --upgrade pip
sudo -EH pip3 install --upgrade distro
sudo -EH pip3 install --upgrade git+https://github.com/fkie-cad/common_helper_files.git
sudo -EH pip3 install --upgrade git+https://github.com/fkie-cad/common_helper_process.git

exit 0
