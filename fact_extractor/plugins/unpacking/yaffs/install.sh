#!/usr/bin/env bash
set -e

echo "------------------------------------"
echo "          install unyaffs           "
echo "------------------------------------"

sudo apt-get install -y unyaffs || exit 1

exit 0
