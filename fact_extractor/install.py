#! /usr/bin/env python3
"""
fact_extractor installer
Copyright (C) 2015-2020  Fraunhofer FKIE

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import logging
import sys
from pathlib import Path

from version import __VERSION__

try:
    import distro

    from helperFunctions.install import OperateInDirectory
    from install.common import main as common
    from install.unpacker import main as unpacker
except (ImportError, ModuleNotFoundError) as error:
    logging.error(f'Could not import install dependencies. Please (re-)run install/pre_install.sh. Error: {error}')
    sys.exit(1)

PROGRAM_NAME = 'FACT_extractor Installer'
PROGRAM_VERSION = __VERSION__
PROGRAM_DESCRIPTION = 'Firmware Analysis and Comparison Tool (FACT) Extractor installation script'

# Compatible Ubuntu releases
FOCAL_CODE_NAMES = ['focal', 'ulyana', 'ulyssa', 'uma', 'una']
JAMMY_CODE_NAMES = ['jammy', 'vanessa', 'vera', 'victoria', 'virginia']
NOBLE_CODE_NAMES = ['noble', 'wilma', 'xia']

# Compatible Debian/Kali releases
BULLSEYE_CODE_NAMES = ['bullseye']
BOOKWORM_CODE_NAMES = ['bookworm', 'kali-rolling']


def _setup_argparser():
    parser = argparse.ArgumentParser(description=f'{PROGRAM_NAME} - {PROGRAM_DESCRIPTION}')
    parser.add_argument('-V', '--version', action='version', version=f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    parser.add_argument('-d', '--debug', action='store_true', help='print debug messages', default=False)
    return parser.parse_args()


def _setup_logging(debug_flag=False):
    log_format = logging.Formatter(
        fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG if debug_flag else logging.INFO)
    console_log.setFormatter(log_format)
    logger.addHandler(console_log)


def check_python_version():
    if sys.version_info.major != 3 or sys.version_info.minor < 9:  # noqa: PLR2004
        sys.exit(f'Error: Incompatible Python version! You need at least version 3.9! Your Version: {sys.version}')


def check_distribution():
    codename = distro.codename().lower()
    if codename in FOCAL_CODE_NAMES:
        logging.debug('Ubuntu 20.04 detected')
        return 'focal'
    if codename in JAMMY_CODE_NAMES:
        logging.debug('Ubuntu 22.04 detected')
        return 'jammy'
    if codename in NOBLE_CODE_NAMES:
        logging.debug('Ubuntu 24.04 detected')
        return 'noble'
    if codename in BULLSEYE_CODE_NAMES:
        logging.debug('Debian 11 detected')
        return 'buster'
    if codename in BOOKWORM_CODE_NAMES:
        logging.debug('Debian 12/Kali detected')
        return 'bullseye'
    sys.exit(
        f'Your Distribution ({distro.id()} {distro.version()}) is not supported. '
        f'FACT Extractor Installer requires Ubuntu 20.04/22.04/24.04, Debian 11/12, Kali or compatible!'
    )


def main():
    check_python_version()
    args = _setup_argparser()
    _setup_logging(debug_flag=args.debug)
    check_distribution()

    logging.info(f'{PROGRAM_NAME} {PROGRAM_VERSION}')
    installation_directory = str(Path(__file__).parent / 'install')

    with OperateInDirectory(installation_directory):
        common()
        unpacker()

    logging.info('installation complete')


if __name__ == '__main__':
    sys.exit(main())
