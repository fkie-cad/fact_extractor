#!/usr/bin/env bash

echo "------------------------------------"
echo "      install password lists        "
echo "------------------------------------"

sudo -EH pip3 install --upgrade git+https://github.com/fkie-cad/common_helper_passwords.git

exit 0