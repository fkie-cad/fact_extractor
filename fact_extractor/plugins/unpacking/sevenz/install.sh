#!/usr/bin/env bash
set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "             install 7z             "
echo "------------------------------------"


# install newest version of 7z
mkdir -p /tmp/fact_build
cd /tmp/fact_build

VERSION_MAJOR="26"
VERSION_MINOR="00"
ARCH=$(uname -m)
if [ "${ARCH}" = "x86_64" ]; then
  ARCH_SUFFIX="x64"
elif [ "${ARCH}" = "aarch64" ]; then
  ARCH_SUFFIX="arm64"
else
  echo "Error: Unsupported architecture ${ARCH}"
  exit 1
fi

FILE="7z${VERSION_MAJOR}${VERSION_MINOR}-linux-${ARCH_SUFFIX}.tar.xz"
URL="https://github.com/ip7z/7zip/releases/download/${VERSION_MAJOR}.${VERSION_MINOR}/${FILE}"
wget "${URL}"
tar xvf "${FILE}" 7zzs
sudo mv 7zzs /usr/local/bin/
rm "${FILE}"

exit 0
