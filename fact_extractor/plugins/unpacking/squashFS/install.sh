#!/usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit

echo "------------------------------------"
echo "   install additional sqfs tools    "
echo "------------------------------------"

sudo apt-get install -y gettext libtool-bin libtool libacl1-dev libcap-dev libc6-dev-i386 lib32ncurses5-dev gcc-multilib lib32stdc++6 gawk pkg-config

sudo useradd -M makeuser

mkdir bin
(
cd bin/ || exit
git clone https://github.com/Freetz/freetz.git
(
cd freetz || exit
sudo chown -R makeuser .
su makeuser -c "umask 0022 && make -j$(nproc) tools"
sudo chown -R "$USER" . || true

cp tools/unsquashfs4-avm-be tools/unsquashfs4-avm-le tools/unsquashfs3-multi ../
cd ..
rm -rf freetz
)
)
sudo userdel makeuser

exit 0

