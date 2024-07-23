#!/usr/bin/env bash
set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "             install 7z             "
echo "------------------------------------"


# install newest version of 7z
mkdir -p /tmp/fact_build
cd /tmp/fact_build
wget https://www.7-zip.org/a/7z2403-linux-x64.tar.xz
tar xvf 7z2403-linux-x64.tar.xz 7zzs
sudo mv 7zzs /usr/local/bin/
rm 7z2403-linux-x64.tar.xz

exit 0
