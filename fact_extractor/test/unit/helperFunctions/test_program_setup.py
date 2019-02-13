import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from helperFunctions.config import get_config_dir
from helperFunctions.program_setup import (
    _load_config, _setup_logging, program_setup
)


class ArgumentMock():
    config_file = '{}/main.cfg'.format(get_config_dir())
    log_level = 'WARNING'
    log_file = '/tmp/fact_test_log'
    silent = False
    debug = False


def test_load_config():
    args = ArgumentMock()
    config = _load_config(args)
    assert config['ExpertSettings']['unpack_threshold'] == '0.8'


def test_setup_logging():
    args = ArgumentMock()
    _setup_logging(args)
    logger = logging.getLogger('')
    assert logger.getEffectiveLevel() == logging.DEBUG
    if Path(args.log_file).is_file():
        Path(args.log_file).unlink()


def test_program_setup():
    tmp_dir = TemporaryDirectory(prefix='fact_test_')
    log_file_path = tmp_dir.name + '/folder/log_file'
    args, _ = program_setup('test', 'test description', command_line_options=['script_name', '--log_file', log_file_path, 'ANY_FILE'])
    assert args.debug is False
    assert os.path.exists(log_file_path)

    tmp_dir.cleanup()
