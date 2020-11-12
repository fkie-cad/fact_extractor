#!/usr/bin/env bash

echo "------------------------------------"
echo "     install liblz4-tools, zstd     "
echo "------------------------------------"

sudo apt-get install -y liblz4-tool zstd
sudo pip3 install --upgrade lz4 git+https://github.com/marin-m/vmlinux-to-elf
exit 0
