#!/usr/bin/env bash
set -eux

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "         install draytex_arsenal    "
echo "------------------------------------"

pip install git+https://github.com/snowy-connection/draytek-arsenal@ef50af366d75a3ae4935a28f489be1b2a6db50a7#subdirectory=draytek_arsenal

exit 0
