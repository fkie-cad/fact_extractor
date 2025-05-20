import argparse
import configparser
import logging
import resource
from pathlib import Path

from common_helper_files import create_dir_for_file

from helperFunctions.config import get_config_dir
from version import __VERSION__


def setup_argparser(name, description, command_line_options, version=__VERSION__):
    parser = argparse.ArgumentParser(description=f'{name} - {description}')
    parser.add_argument('-V', '--version', action='version', version=f'{name} {version}')
    parser.add_argument('-l', '--log_file', help='path to log file', default=None)
    parser.add_argument(
        '-L', '--log_level', help='define the log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default=None
    )
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='print debug messages')
    parser.add_argument('-C', '--config_file', help='set path to config File', default=f'{get_config_dir()}/main.cfg')
    parser.add_argument(
        '-p',
        '--password-list',
        help='path to a password list for archive password cracking',
        type=Path,
    )
    parser.add_argument('FILE_PATH', type=str, help='Path to file that should be extracted')
    return parser.parse_args(command_line_options[1:])


def setup_logging(debug, log_file=None, log_level=None):
    log_format = logging.Formatter(
        fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    if log_file:
        create_dir_for_file(log_file)
        file_log = logging.FileHandler(log_file)
        file_log.setLevel(log_level or logging.WARNING)
        file_log.setFormatter(log_format)
        logger.addHandler(file_log)

    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG if debug else log_level or logging.INFO)
    console_log.setFormatter(log_format)
    logger.addHandler(console_log)


def check_ulimits():
    # Get number of openable files
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    if soft < 1024:  # noqa: PLR2004
        resource.setrlimit(resource.RLIMIT_NOFILE, (min(1024, hard), hard))
        logging.info(f'The number of openable files has been raised from {soft} to {min(1024, hard)}.')
    elif soft == resource.RLIM_INFINITY or soft > 100000:  # noqa: PLR2004
        logging.warning('Warning: A very high (or no) nofile limit will slow down fakeroot and cause other problems.')


def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config
