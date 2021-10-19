#!/usr/bin/env python3
'''
    fact_extractor
    Copyright (C) 2015-2019  Fraunhofer FKIE

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
from pathlib import Path
from re import match
import sys

from common_helper_process import execute_shell_command_get_return_code

from helperFunctions.config import get_config_dir
from helperFunctions.program_setup import load_config, setup_logging
from unpacker.unpack import unpack


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chown', type=str, default='',
                        help='change back ownership of output files to <user id>:<group id>')
    parser.add_argument('--extract_everything', action='store_true', default=False,
                        help='change the behavior of the extractor: extract also empty files and duplicates')
    return parser.parse_args()


def _change_owner_of_output_files(files_dir: Path, owner: str) -> int:
    if not match(r'\d+:\d+', owner):
        logging.error('ownership string should have the format <user id>:<group id>')
        return 1

    _, return_code_chown = execute_shell_command_get_return_code(f'sudo chown -R {owner} {files_dir}')
    _, return_code_chmod = execute_shell_command_get_return_code(f'sudo chmod -R u+rw {files_dir}')
    return return_code_chmod | return_code_chown


def main(args):
    config = load_config(f'{get_config_dir()}/main.cfg')
    setup_logging(debug=False)

    input_dir = Path(config.get('unpack', 'data_folder'), 'input')
    input_file = list(input_dir.iterdir())[0]

    unpack(input_file, config, args.extract_everything )

    if args.chown:
        output_dir = Path(config.get('unpack', 'data_folder'), 'files')
        return _change_owner_of_output_files(output_dir, args.chown)

    return 0


if __name__ == '__main__':
    sys.exit(main(_parse_args()))
