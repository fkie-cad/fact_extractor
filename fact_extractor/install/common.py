import logging
import os
from contextlib import suppress
from pathlib import Path

from helperFunctions.config import load_config
from helperFunctions.install import (
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


def install_apt_dependencies(distribution: str):
    apt_install_packages(*APT_DEPENDENCIES['common'])
    apt_install_packages(*APT_DEPENDENCIES[distribution])


def main(distribution):
    logging.info('Updating package lists')
    apt_update_sources()

    # install dependencies
    install_apt_dependencies(distribution)
    pip_install_packages(*load_requirements_file(PIP_DEPENDENCY_FILE))

    # make bin dir
    with suppress(FileExistsError):
        os.mkdir('../bin')

    config = load_config('main.cfg')
    data_folder = config.get('unpack', 'data_folder')
    os.makedirs(str(Path(data_folder, 'files')), exist_ok=True)
    os.makedirs(str(Path(data_folder, 'reports')), exist_ok=True)

    return 0
