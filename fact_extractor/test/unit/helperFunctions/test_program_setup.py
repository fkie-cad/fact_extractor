import logging
from pathlib import Path

from fact_extractor.helperFunctions.config import get_config_dir
from fact_extractor.helperFunctions.program_setup import (
    load_config, setup_logging, setup_argparser
)


class ArgumentMock():
    config_file = '{}/main.cfg'.format(get_config_dir())
    log_level = 'WARNING'
    log_file = '/tmp/fact_test_log'
    silent = False
    debug = False


def test_load_config():
    config = load_config('{}/main.cfg'.format(get_config_dir()))
    assert config['ExpertSettings']['unpack_threshold'] == '0.8'


def test_setup_logging():
    args = ArgumentMock()
    setup_logging(args)
    logger = logging.getLogger('')
    assert logger.getEffectiveLevel() == logging.DEBUG
    if Path(args.log_file).is_file():
        Path(args.log_file).unlink()


def test_setup_argparser():
    log_file_path = 'any/given/path'
    args = setup_argparser('test', 'test description', command_line_options=['script_name', '--log_file', log_file_path, 'ANY_FILE'])

    assert args.debug is False
    assert args.log_file == log_file_path
    assert args.log_level is None
