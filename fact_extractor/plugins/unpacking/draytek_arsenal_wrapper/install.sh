#!/usr/bin/env bash
set -eux

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "------------------------------------"
echo "         install draytex_arsenal    "
echo "------------------------------------"

pip install git+https://github.com/snowy-connection/draytek-arsenal@23f3469b303a0adc285d5e3f32e94e5bfe4aae82#subdirectory=draytek_arsenal

exit 0
