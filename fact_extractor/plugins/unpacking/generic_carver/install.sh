#!/usr/bin/env bash

# This setup is largely ripped of from emba @ https://github.com/e-m-b-a/emba/blob/master/installer/IP61_unblob.sh
# Thanks to m-1-k-3 and the emba team!

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1

echo "------------------------------------"
echo "     install unblob via poetry      "
echo "------------------------------------"

sudo -EH apt-get install -y e2fsprogs img2simg lziprecover xz-utils libmagic1 libhyperscan5

curl -L -o sasquatch_1.0_amd64.deb https://github.com/onekey-sec/sasquatch/releases/download/sasquatch-v1.0/sasquatch_1.0_amd64.deb
sudo dpkg -i sasquatch_1.0_amd64.deb
rm -f sasquatch_1.0_amd64.deb

git clone https://github.com/onekey-sec/unblob.git

# install poetry
sudo -EH pip3 install --upgrade poetry
cd unblob || exit 1

# install unblob with poetry:
poetry install --only main
UNBLOB_PATH=$(poetry env info --path)

if [[ -f "$UNBLOB_PATH""/bin/unblob" ]]; then
  if [[ ! -f "/usr/local/bin/unblob" ]]; then
    sudo ln -s "$UNBLOB_PATH""/bin/unblob" /usr/local/bin/unblob
  fi
else
  echo "Could not install unblob" && exit 1
fi

rm -r tests

exit 0
