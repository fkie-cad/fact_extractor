import logging
import os
from contextlib import suppress
from pathlib import Path

from helperFunctions.config import load_config
from helperFunctions.install import (
    apt_install_packages, apt_update_sources, pip3_install_packages
)


def main(distribution):
    xenial = distribution == 'xenial'

    logging.info('Updating package lists')
    apt_update_sources()

    # Non python dependencies
    apt_install_packages('build-essential', 'automake', 'autoconf', 'libtool')

    # python dependencies
    apt_install_packages('python3', 'python3-dev', 'python', 'python-dev', 'python-wheel', 'python-setuptools')

    pip3_install_packages('pytest', 'pytest-cov', 'pytest-flake8')
    if not xenial:
        pip3_install_packages('testresources')

    # make bin dir
    with suppress(FileExistsError):
        os.mkdir('../bin')

    config = load_config('main.cfg')
    data_folder = config.get('unpack', 'data_folder')
    os.makedirs(str(Path(data_folder, 'files')), exist_ok=True)
    os.makedirs(str(Path(data_folder, 'reports')), exist_ok=True)

    pip3_install_packages('flask', 'flask_restful')

    return 0
