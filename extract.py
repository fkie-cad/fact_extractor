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


def container_exists(container):
    return subprocess.run('docker history {}'.format(container), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0


def call_docker(input_file, container, target):
    tmpdir = TemporaryDirectory()
    tmp = tmpdir.name

    for subpath in ['files', 'reports', 'input']:
        Path(tmp, subpath).mkdir()

    shutil.copy(input_file, str(Path(tmp, 'input', Path(input_file).name)))

    subprocess.run('docker run --rm -v {}:/tmp/extractor -v /dev:/dev --privileged {}'.format(tmp, container), shell=True)

    shutil.copytree(str(Path(tmp, 'files')), target)

    try:
        tmpdir.cleanup()
    except PermissionError:
        print('Cleanup requires root. If you would be so kind..')
        subprocess.run('sudo rm -rf {}'.format(tmpdir.name), shell=True)
        tmpdir.cleanup()


def main():
    arguments = parse_arguments()

    output_directory = arguments.output_directory if arguments.output_directory else str(Path(__file__).parent / 'extracted_files')
    if Path(output_directory).exists():
        print('Target directory exists ({}). Please choose a non-existing directory with -o option.'.format(output_directory))
        return 1

    if not container_exists(arguments.container):
        print('Container {} doesn\'t exist. Please specify an existing container with the -c option.'.format(arguments.container))
        return 1

    if not Path(arguments.ARCHIVE[0]).is_file():
        print('Given input file {} doesn\'t exist. Please give an existing path.'.format(arguments.ARCHIVE[0]))

    call_docker(arguments.ARCHIVE[0], arguments.container, output_directory)

    return 0


if __name__ == '__main__':
    sys.exit(main())
