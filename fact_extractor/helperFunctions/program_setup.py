
import argparse
import configparser
import logging
import sys

from common_helper_files import create_dir_for_file
from helperFunctions.config import get_config_dir
from version import __VERSION__


def program_setup(name, description, docker=False, version=__VERSION__, command_line_options=sys.argv):  # pylint: disable=dangerous-default-value
    args = _setup_argparser(name, description, docker=docker, command_line_options=command_line_options, version=version)
    config = _load_config(args)
    _setup_logging(args)
    return args, config


def _setup_argparser(name, description, docker, command_line_options, version=__VERSION__):
    parser = argparse.ArgumentParser(description='{} - {}'.format(name, description))
    parser.add_argument('-V', '--version', action='version', version='{} {}'.format(name, version))
    parser.add_argument('-l', '--log_file', help='path to log file', default=None)
    parser.add_argument('-L', '--log_level', help='define the log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default=None)
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='print debug messages')
    parser.add_argument('-C', '--config_file', help='set path to config File', default='{}/main.cfg'.format(get_config_dir()))
    if not docker:
        parser.add_argument('FILE_PATH', type=str, help='Path to file that should be extracted')
    return parser.parse_args(command_line_options[1:])


def _setup_logging(args):
    log_level = args.log_level if args.log_level else logging.WARNING
    log_format = logging.Formatter(fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    if args.log_file:
        create_dir_for_file(args.log_file)
        file_log = logging.FileHandler(args.log_file)
        file_log.setLevel(log_level)
        file_log.setFormatter(log_format)
        logger.addHandler(file_log)

    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG if args.debug else logging.INFO)
    console_log.setFormatter(log_format)
    logger.addHandler(console_log)


def _load_config(args):
    config = configparser.ConfigParser()
    config.read(args.config_file)
    return config
