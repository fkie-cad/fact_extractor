#!/usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "        install uefi parser         "
echo "------------------------------------"

cd ../../../install

git clone https://github.com/theopolis/uefi-firmware-parser.git
cd uefi-firmware-parser
git checkout 4262dbbaab12c964242545e4f59a74c8f1b2f871 # known stable commit
wget https://patch-diff.githubusercontent.com/raw/theopolis/uefi-firmware-parser/pull/83.patch # patch for python3 compatibilty
git apply 83.patch
sudo -E python3 setup.py install --force
cp bin/uefi-firmware-parser ../../bin
cd ..
sudo rm -rf uefi-firmware-parser

exit 0
