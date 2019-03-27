#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def parse_arguments():
    parser = argparse.ArgumentParser(description='FACT extractor CLI')
    parser.add_argument('-c', '--container', help='docker container', default='fkiecad/fact_extractor')
    parser.add_argument('-o', '--output_directory', help='path to extracted files', default=None)
    parser.add_argument('ARCHIVE', type=str, nargs=1, help='Archive for extraction')

    return parser.parse_args()


def call_docker(input_file, container, target):
    tmpdir = TemporaryDirectory()
    tmp = tmpdir.name

    for subpath in ['files', 'reports', 'input']:
        Path(tmp, subpath).mkdir()

    shutil.copy(input_file, str(Path(tmp, 'input', Path(input_file).name)))

    subprocess.run('docker run --rm -v {}:/tmp/extractor -v /dev:/dev --privileged {}'.format(tmp, container), shell=True)

    print('Moving files to {}'.format(target))
    shutil.copytree(str(Path(tmp, 'files')), target)

    try:
        tmpdir.cleanup()
    except PermissionError:
        subprocess.run('sudo rm -rf {}'.format(tmpdir.name), shell=True)
        tmpdir.cleanup()


def main():
    arguments = parse_arguments()

    output_directory = arguments.output_directory if arguments.output_directory else str(Path(__file__).parent / 'extracted_files')

    call_docker(arguments.ARCHIVE[0], arguments.container, output_directory)


if __name__ == '__main__':
    sys.exit(main())
