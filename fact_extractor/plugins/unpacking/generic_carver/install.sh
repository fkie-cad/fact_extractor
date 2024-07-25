#!/usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1

echo "------------------------------------"
echo "    install unblob dependencies     "
echo "------------------------------------"

sudo -EH apt-get install -y e2fsprogs img2simg lziprecover xz-utils libmagic1 libhyperscan5

curl -L -o sasquatch_1.0_amd64.deb https://github.com/onekey-sec/sasquatch/releases/download/sasquatch-v1.0/sasquatch_1.0_amd64.deb
sudo dpkg -i sasquatch_1.0_amd64.deb
rm -f sasquatch_1.0_amd64.deb

exit 0
