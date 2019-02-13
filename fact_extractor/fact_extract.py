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

import logging
from pathlib import Path

from helperFunctions.program_setup import program_setup
from unpacker.unpack import Unpacker


def extract(file_path, config):
    unpacker = Unpacker(config)

    extracted_objects = unpacker.unpack(file_path)
    logging.info('unpacking of {} complete: {} files extracted'.format(Path(file_path).name, len(extracted_objects)))

    for extracted_object in extracted_objects:
        print(extracted_object)


def main():
    arguments, config = program_setup('FACT extractor', 'Standalone extraction utility')
    extract(arguments.FILE_PATH, config)

    return 0


if __name__ == '__main__':
    exit(main())
