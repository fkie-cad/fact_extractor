#!/usr/bin/env bash
set -eux

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "         install boschtool          "
echo "------------------------------------"

wget https://github.com/anvilventures/BoschFirmwareTool/releases/download/v1.0.0/boschfwtool-linux-x64.tar.gz
mkdir -p bin
tar xf boschfwtool-linux-x64.tar.gz -C bin
rm boschfwtool-linux-x64.tar.gz

exit 0
