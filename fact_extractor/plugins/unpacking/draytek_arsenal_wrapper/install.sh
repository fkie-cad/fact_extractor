#!/usr/bin/env bash
set -eux

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "         install draytex_arsenal    "
echo "------------------------------------"

pip install git+https://github.com/snowy-connection/draytek-arsenal@216729aefdcb1073d56d9939078ad74c866be8be#subdirectory=draytek_arsenal

exit 0
