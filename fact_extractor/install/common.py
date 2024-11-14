import logging
import subprocess as sp
from pathlib import Path

from helperFunctions.config import load_config
from helperFunctions.install import (
    OperateInDirectory,
    apt_install_packages,
    apt_update_sources,
    load_requirements_file,
    pip_install_packages,
)

APT_DEPENDENCIES = {
    # Ubuntu
    'bionic': [],
    'focal': [],
    'jammy': [],
    # Debian
    'buster': [],
    'bullseye': [],
    # Packages common to all platforms
    'common': [
        # Non python dependencies
        'build-essential',
        'automake',
        'autoconf',
        'libtool',
        # Python dependencies
        'python3',
        'python3-dev',
        'python-wheel-common',
    ],
}
PIP_DEPENDENCY_FILE = Path(__file__).parent.parent.parent / 'requirements-common.txt'
BIN_DIR = Path(__file__).parent.parent / 'bin'


def install_apt_dependencies(distribution: str):
    apt_install_packages(*APT_DEPENDENCIES['common'])
    apt_install_packages(*APT_DEPENDENCIES[distribution])


def _install_magic():
    with OperateInDirectory(BIN_DIR):
        sp.run(
            [
                'wget',
                '--output-document',
                'firmware.xz',
                'https://github.com/fkie-cad/firmware-magic-database/releases/download/v0.2.1/firmware.xz',
            ],
            check=True,
        )
        sp.run(
            [
                'unxz',
                '--force',
                'firmware.xz',
            ],
            check=False,
        )


def main(distribution):
    logging.info('Updating package lists')
    apt_update_sources()

    # install dependencies
    install_apt_dependencies(distribution)
    pip_install_packages(*load_requirements_file(PIP_DEPENDENCY_FILE))

    BIN_DIR.mkdir(exist_ok=True)

    _install_magic()

    config = load_config('main.cfg')
    data_folder = config.get('unpack', 'data_folder')
    Path(data_folder, 'files').mkdir(parents=True, exist_ok=True)
    Path(data_folder, 'reports').mkdir(exist_ok=True)

    return 0
