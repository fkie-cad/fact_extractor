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

import sys
from pathlib import Path

from fact_extractor.helperFunctions.file_system import change_owner_of_output_files
from fact_extractor.helperFunctions.program_setup import setup_argparser, setup_logging, load_config, check_ulimits
from fact_extractor.unpacker.unpack import unpack


def main():
    arguments = setup_argparser('FACT extractor', 'Standalone extraction utility', sys.argv)
    config = load_config(arguments.config_file)
    setup_logging(arguments.debug, log_file=arguments.log_file, log_level=arguments.log_level)
    check_ulimits()

    data_dir = Path(config.get('unpack', 'data_folder'))
    report_dir = data_dir / 'reports'
    files_dir = data_dir / 'files'

    # Make sure report folder exists some meta.json can be written
    report_dir.mkdir(parents=True, exist_ok=True)

    unpack(arguments.FILE_PATH, config)

    if arguments.chown is not None:
        change_owner_of_output_files(files_dir, arguments.chown)

    return 0

sys.exit(main())
