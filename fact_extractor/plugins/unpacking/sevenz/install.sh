#!/usr/bin/env bash
set -euo pipefail

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "             install 7z             "
echo "------------------------------------"

VERSION="2407"
ARCH=$(uname -m)
if [[ $ARCH == "x86_64" ]]; then
    ARCH_SUFFIX="x64"
elif [[ $ARCH == "aarch64" ]]; then
    ARCH_SUFFIX="arm64"
else
    echo "unsupported architecture ${ARCH}"
    exit 1
fi
FILE="7z${VERSION}-linux-${ARCH_SUFFIX}.tar.xz"

mkdir -p /tmp/fact_build
cd /tmp/fact_build
wget "https://www.7-zip.org/a/${FILE}"
tar xvf "${FILE}" 7zzs
sudo mv 7zzs /usr/local/bin/7z
rm "${FILE}"

exit 0
