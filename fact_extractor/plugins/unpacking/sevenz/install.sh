#!/usr/bin/env bash
set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "             install 7z             "
echo "------------------------------------"

VERSION="2407"
FILE="7z${VERSION}-linux-x64.tar.xz"

# install newest version of 7z
mkdir -p /tmp/fact_build
cd /tmp/fact_build
wget "https://www.7-zip.org/a/${FILE}"
tar xvf "${FILE}" 7zzs
sudo mv 7zzs /usr/local/bin/
rm "${FILE}"

exit 0
