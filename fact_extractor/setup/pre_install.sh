#!/usr/bin/env bash
set -euxo pipefail

echo "Install Pre-Install Requirements"
(apt-get update && apt-get install -y sudo) || true

sudo apt-get update
sudo apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gcc \
  git \
  libmagic-dev \
  python3-dev \
  python3-venv \
  software-properties-common \
  wget \
  xz-utils
