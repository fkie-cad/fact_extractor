import logging
import os
from contextlib import suppress
from pathlib import Path

from helperFunctions.config import load_config
from helperFunctions.install import apt_install_packages, apt_update_sources, pip_install_packages


DEPENDENCIES = {
    # Ubuntu
    'bionic': {},
    'focal': {},
    'jammy': {},
    # Debian
    'buster': {},
    'bullseye': {},
    # Packages common to all platforms
    'common': {
        'apt': [
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
        'pip3': [
            'flask',
            'flask_restful',
            'gunicorn',
            'pytest',
            'pytest-cov',
            'testresources',
        ],
    },
}


def install_dependencies(dependencies):
    apt = dependencies.get('apt', [])
    pip3 = dependencies.get('pip3', [])
    apt_install_packages(*apt)
    pip_install_packages(*pip3)


def main(distribution):
    logging.info('Updating package lists')
    apt_update_sources()

    # install dependencies
    install_dependencies(DEPENDENCIES['common'])
    install_dependencies(DEPENDENCIES[distribution])

    # make bin dir
    with suppress(FileExistsError):
        os.mkdir('../bin')

    config = load_config('main.cfg')
    data_folder = config.get('unpack', 'data_folder')
    os.makedirs(str(Path(data_folder, 'files')), exist_ok=True)
    os.makedirs(str(Path(data_folder, 'reports')), exist_ok=True)

    return 0
