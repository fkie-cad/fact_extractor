import logging
import os
from contextlib import suppress
from pathlib import Path

from helperFunctions.config import load_config
from helperFunctions.install import (
    apt_install_packages, apt_update_sources, pip2_install_packages, pip3_install_packages
)


DEPENDENCIES = {
    # Ubuntu
    'xenial': {
        'apt': [
            'python-wheel'
        ]
    },
    'bionic': {
        'apt': [
            'python-wheel'
        ],
        'pip3': [
            'testresources'
        ]
    },
    'focal': {
        'apt': [
            'python3-wheel',
            'python-wheel-common'
        ],
        'pip3': [
            'testresources'
        ]
    },
    # Debian
    'buster': {
        'apt': [
            'python-wheel'
        ],
        'pip3': [
            'testresources'
        ]
    },
    'bullseye': {
        'apt': [
            'python3-wheel',
            'python-wheel-common'
        ],
        'pip3': [
            'testresources'
        ]
    },
    # Packages common to all plateforms
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
            'python',
            'python-dev',
            'python-setuptools'
        ],
        'pip2': [],
        'pip3': [
            'pytest',
            'pytest-cov',
            'pytest-flake8'
        ]
    }
}


def install_dependencies(dependencies):
    apt = dependencies.get('apt', [])
    pip2 = dependencies.get('pip2', [])
    pip3 = dependencies.get('pip3', [])
    apt_install_packages(*apt)
    pip2_install_packages(*pip2)
    pip3_install_packages(*pip3)


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
