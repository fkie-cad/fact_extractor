import logging
from pathlib import Path

from helperFunctions.config import load_config
from helperFunctions.install import (
    apt_install_packages,
    apt_update_sources,
    load_requirements_file,
    pip_install_packages,
)

APT_DEPENDENCIES = [
    # Non python dependencies
    'build-essential',
    'automake',
    'autoconf',
    'libtool',
]

PIP_DEPENDENCY_FILE = Path(__file__).parent.parent.parent / 'requirements-common.txt'


def install_apt_dependencies():
    apt_install_packages(*APT_DEPENDENCIES)


def main():
    logging.info('Updating package lists')
    apt_update_sources()

    # install dependencies
    install_apt_dependencies()
    pip_install_packages(*load_requirements_file(PIP_DEPENDENCY_FILE))

    # make bin dir
    Path('../bin').mkdir(exist_ok=True)

    config = load_config('main.cfg')
    data_folder = config.get('unpack', 'data_folder')
    Path(data_folder, 'files').mkdir(parents=True, exist_ok=True)
    Path(data_folder, 'reports').mkdir(parents=True, exist_ok=True)

    return 0
