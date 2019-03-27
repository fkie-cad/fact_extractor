#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from tempfile import TemporaryDirectory


def parse_arguments():
    parser = argparse.ArgumentParser(description='FACT extractor CLI')
    parser.add_argument('-c', '--container', help='docker container', default='fkiecad/fact_extractor')
    parser.add_argument('-o', '--output_directory', help='path to extracted files', default=None)
    parser.add_argument('-r', '--report_file', help='write report to a file', default=None)
    parser.add_argument('ARCHIVE', type=str, nargs=1, help='Archive for extraction')

    return parser.parse_args()


def container_exists(container):
    return subprocess.run('docker history {}'.format(container), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0


def call_docker(input_file, container, target, report_file):
    tmpdir = TemporaryDirectory()
    tmp = tmpdir.name

    for subpath in ['files', 'reports', 'input']:
        Path(tmp, subpath).mkdir()

    shutil.copy(input_file, str(Path(tmp, 'input', Path(input_file).name)))

    subprocess.run('docker run --rm -v {}:/tmp/extractor -v /dev:/dev --privileged {}'.format(tmp, container), shell=True)

    print('Now taking ownership of the files. You may need to enter your password.')
    subprocess.run('sudo chown -R {} {}'.format(os.environ['USER'], tmpdir.name), shell=True)

    with suppress(shutil.Error):
        shutil.copytree(str(Path(tmp, 'files')), target)

    indented_report = json.dumps(json.loads(Path(tmp, 'reports', 'meta.json').read_text()), indent=4)
    if report_file:
        Path(report_file).write_text(indented_report)
    else:
        print(indented_report)

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

    if arguments.report_file and not Path(arguments.report_file).parent.is_dir():
        print('Report file ({}) can not be created. Check if parent directory exists.'.format(arguments.report_file))
        return 1
    if arguments.report_file and Path(arguments.report_file).exists():
        print('Warning: Report file will be overwritten.')

    call_docker(arguments.ARCHIVE[0], arguments.container, output_directory, arguments.report_file)

    return 0


if __name__ == '__main__':
    sys.exit(main())
