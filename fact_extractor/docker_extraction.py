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
from pathlib import Path
import sys

from helperFunctions.config import load_config
from helperFunctions.file_system import change_owner_of_output_files
from helperFunctions.program_setup import check_ulimits, setup_logging
from unpacker.unpack import unpack


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--chown', type=str, default='', help='change back ownership of output files to <user id>:<group id>'
    )
    parser.add_argument(
        '--extract_everything',
        action='store_true',
        default=False,
        help='change the behavior of the extractor: extract also empty files',
    )
    return parser.parse_args()


def main(args):
    config = load_config()
    setup_logging(debug=False)
    check_ulimits()

    data_folder = Path(config.unpack.data_folder)
    input_dir = data_folder / 'input'
    input_file = list(input_dir.iterdir())[0]

    unpack(input_file, config, args.extract_everything)

    if args.chown:
        output_dir = data_folder / 'files'
        return change_owner_of_output_files(output_dir, args.chown)

    return 0


if __name__ == '__main__':
    sys.exit(main(_parse_args()))
