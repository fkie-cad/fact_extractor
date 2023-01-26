#!/usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit

echo "------------------------------------"
echo "     install phantom fw tools       "
echo "------------------------------------"

cd ../../../install || exit

git clone https://github.com/mefistotelis/phantom-firmware-tools.git
cd phantom-firmware-tools || exit
mv dji_xv4_fwcon.py ../../bin/
mv amba_fwpak.py ../../bin/
mv amba_romfs.py ../../bin/
cd ..
rm -rf phantom-firmware-tools

exit 0
