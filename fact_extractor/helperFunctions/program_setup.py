import argparse
import configparser
import logging

from common_helper_files import create_dir_for_file

from helperFunctions.config import get_config_dir
from version import __VERSION__


def setup_argparser(name, description, command_line_options, version=__VERSION__):
    parser = argparse.ArgumentParser(description='{} - {}'.format(name, description))
    parser.add_argument('-V', '--version', action='version', version='{} {}'.format(name, version))
    parser.add_argument('-l', '--log_file', help='path to log file', default=None)
    parser.add_argument('-L', '--log_level', help='define the log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default=None)
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='print debug messages')
    parser.add_argument('-C', '--config_file', help='set path to config File', default='{}/main.cfg'.format(get_config_dir()))
    parser.add_argument('FILE_PATH', type=str, help='Path to file that should be extracted')
    return parser.parse_args(command_line_options[1:])


def setup_logging(debug, log_file=None, log_level=None):
    log_level = log_level if log_level else logging.WARNING
    log_format = logging.Formatter(fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    if log_file:
        create_dir_for_file(log_file)
        file_log = logging.FileHandler(log_file)
        file_log.setLevel(log_level)
        file_log.setFormatter(log_format)
        logger.addHandler(file_log)

    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG if debug else logging.INFO)
    console_log.setFormatter(log_format)
    logger.addHandler(console_log)


def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config
