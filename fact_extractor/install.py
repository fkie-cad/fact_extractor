#! /usr/bin/env python3
'''
    FACT Installer
    Copyright (C) 2015-2018  Fraunhofer FKIE

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
'''

import argparse
import logging
import os
import sys
from pathlib import Path

try:
    import distro

    from common_helper_process import execute_shell_command_get_return_code

    from helperFunctions.install import OperateInDirectory
    from install.common import main as common
    from install.backend import main as backend
except ImportError:
    sys.exit('Could not import install dependencies. Please (re-)run install/pre_install.sh')

PROGRAM_NAME = 'FACT_extraction Installer'
PROGRAM_VERSION = '0.1'
PROGRAM_DESCRIPTION = 'Firmware Analysis and Comparison Tool (FACT) Extractor installation script'

BIONIC_CODE_NAMES = ['bionic', 'tara']
XENIAL_CODE_NAMES = ['xenial', 'yakkety', 'sarah', 'serena', 'sonya', 'sylvia']


def _setup_argparser():
    parser = argparse.ArgumentParser(description='{} - {}'.format(PROGRAM_NAME, PROGRAM_DESCRIPTION))
    parser.add_argument('-V', '--version', action='version', version='{} {}'.format(PROGRAM_NAME, PROGRAM_VERSION))
    logging_options = parser.add_argument_group('Logging and Output Options')
    logging_options.add_argument('-l', '--log_file', help='path to log file', default='./install.log')
    logging_options.add_argument('-L', '--log_level', help='define the log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='WARNING')
    logging_options.add_argument('-d', '--debug', action='store_true', help='print debug messages', default=False)
    return parser.parse_args()


def _get_console_output_level(debug_flag):
    if debug_flag:
        return logging.DEBUG
    else:
        return logging.INFO


def _setup_logging(args, debug_flag=False):
    try:
        log_level = getattr(logging, args.log_level, None)
        log_format = logging.Formatter(fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logger = logging.getLogger('')
        logger.setLevel(logging.DEBUG)
        create_dir_for_file(args.log_file, dir_description='logging directory')
        file_log = logging.FileHandler(args.log_file)
        file_log.setLevel(log_level)
        file_log.setFormatter(log_format)
        console_log = logging.StreamHandler()
        console_log.setLevel(_get_console_output_level(debug_flag))
        console_log.setFormatter(log_format)
        logger.addHandler(file_log)
        logger.addHandler(console_log)
    except Exception as e:
        sys.exit('Error: Could not setup logging: {} {}'.format(sys.exc_info()[0].__name__, e))


def create_dir_for_file(file_path, dir_description='directory'):
    '''
    Creates the directory of the file_path.
    '''
    directory = os.path.dirname(os.path.abspath(file_path))
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        sys.exit('Error: Could not create {}: {} {}'.format(dir_description, sys.exc_info()[0].__name__, e))


def welcome():
    logging.info('{} {}'.format(PROGRAM_NAME, PROGRAM_VERSION))


def check_python_version():
    if sys.version_info.major != 3 or sys.version_info.minor < 5:
        sys.exit('Error: Incompatible Python version! You need at least version 3.5! Your Version: {}'.format(sys.version))


def check_distribution():
    codename = distro.codename().lower()
    if codename in XENIAL_CODE_NAMES:
        logging.debug('Ubuntu 16.04 detected')
        return 'xenial'
    if codename in BIONIC_CODE_NAMES:
        logging.debug('Ubuntu 18.04 detected')
        return 'bionic'
    else:
        sys.exit('Your Distribution ({} {}) is not supported. FACT Installer requires Ubuntu 16.04, Ubuntu 18.04 or compatible!'.format(distro.id(), distro.version()))


if __name__ == '__main__':
    check_python_version()
    args = _setup_argparser()
    _setup_logging(args, debug_flag=args.debug)
    welcome()
    distribution = check_distribution()

    installation_directory = str(Path(Path(__file__).parent, 'install').absolute())

    with OperateInDirectory(installation_directory):
        common(distribution)
        backend(distribution)

    logging.info('installation complete')

    sys.exit()
