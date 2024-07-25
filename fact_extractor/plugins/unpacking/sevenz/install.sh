#!/usr/bin/env bash
set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "      install p7z from source       "
echo "------------------------------------"


# install newest version of p7zip
sudo apt-get remove -y p7zip-full

mkdir -p /tmp/fact_build
cd /tmp/fact_build

wget -O 7zip.tar.bz2 https://sourceforge.net/projects/p7zip/files/latest/download
# remove possible artifacts from previous installation (: == NOP)
rm -rf ./p7zip* || :
tar xvjf 7zip.tar.bz2
cd p7zip*
# gcc >= 11 has -Wnarrowing as default flag which leads to an error during compilation
# g++ will try to use standard C++17 but the code is not compatible -> use C++14
sed -i 's/CXXFLAGS=-c -I. \\/CXXFLAGS=-c -I. -Wno-narrowing -std=c++14 \\/g' makefile.glb  || echo "Warning: Could not apply makefile patch"
cp makefile.linux_any_cpu makefile.machine
make -j"$(nproc)" all3
sudo ./install.sh
cd ..
rm -fr p7zip* 7zip.tar.bz2

exit 0
