#!/usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1

echo "------------------------------------"
echo "         install boschtool          "
echo "------------------------------------"

wget https://github.com/anvilventures/BoschFirmwareTool/releases/download/v1.0.0/boschfwtool-linux-x64.tar.gz || exit 1
mkdir bin
tar xf boschfwtool-linux-x64.tar.gz -C bin || exit 1
rm boschfwtool-linux-x64.tar.gz

exit 0
