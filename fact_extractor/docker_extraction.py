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

from pathlib import Path

from helperFunctions.config import get_config_dir
from helperFunctions.program_setup import load_config, setup_logging
from unpacker.unpack import unpack


def main():
    config = load_config('{}/main.cfg'.format(get_config_dir()))
    setup_logging(debug=False)

    input_dir = Path(config.get('unpack', 'data_folder'), 'input')
    input_file = list(input_dir.iterdir())[0]

    unpack(input_file, config)

    return 0


if __name__ == '__main__':
    exit(main())
