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

import os
import sys
from pathlib import Path

from helperFunctions.program_setup import setup_argparser, setup_logging, load_config
from unpacker.unpack import unpack


def main():
    arguments = setup_argparser('FACT extractor', 'Standalone extraction utility', sys.argv)
    config = load_config(arguments.config_file)
    setup_logging(arguments.debug, log_file=arguments.log_file, log_level=arguments.log_level)

    # Make sure report folder exists some meta.json can be written
    report_folder = Path(config.get('unpack', 'data_folder'), 'reports')
    report_folder.mkdir(parents=True, exist_ok=True)
    unpack(arguments.FILE_PATH, config)

    return 0


if __name__ == '__main__':
    exit(main())
