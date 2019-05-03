#!/usr/bin/env python3

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from tempfile import TemporaryDirectory

VERSION = '0.1'
NAME = 'FACT_extractor interface'
DEFAULT_CONTAINER = 'fkiecad/fact_extractor'


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Command line interface for FACT_extractor.\nExtract arbitrary container or compression formats with one utility.'
    )
    parser.add_argument('-v', '--version', action='version', version=set_version())
    parser.add_argument('-c', '--container', help='docker container', default=DEFAULT_CONTAINER)
    parser.add_argument('-m', '--memory', help='memory limit for docker container (in MB)', default='512')
    parser.add_argument('-o', '--output_directory', help='path to extracted files', default=None)
    parser.add_argument('-r', '--report_file', help='write report to a file', default=None)
    parser.add_argument('-V', '--verbose', action='store_true', default=False, help='increase verbosity')
    parser.add_argument('FILE', type=str, nargs=1, help='File for extraction')
    return parser.parse_args()


def setup_logging(verbose):
    console_log = logging.StreamHandler()
    console_log.setFormatter(
        logging.Formatter(fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    )

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.addHandler(console_log)


def container_exists(container):
    return subprocess.run('docker history {}'.format(container), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).returncode == 0


def default_container_status():
    try:
        process_result = subprocess.run(
            'docker image ls {} --format "{{{{.Tag}}}},{{{{.CreatedAt}}}}"'.format(DEFAULT_CONTAINER), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        tag, creation_time = process_result.stdout.decode().strip().split(',')
    except ValueError:
        tag, creation_time = 'n/e', 'n/e'
    return tag, creation_time


def set_version():
    container_tag, container_creation = default_container_status()

    return '{}\nProgramm version:\t0.1\nDefault container:\t{}\nContainer tag:\t\t{}\nContainer creation:\t{}'.format(
        NAME,
        DEFAULT_CONTAINER,
        container_tag,
        container_creation
    )


def call_docker(input_file, container, target, report_file, memory_limit, tmpdir=None):
    tmpdir = tmpdir if tmpdir else TemporaryDirectory()

    for subpath in ['files', 'reports', 'input']:
        Path(tmpdir.name, subpath).mkdir(exist_ok=True)

    shutil.copy(input_file, str(Path(tmpdir.name, 'input', Path(input_file).name)))

    subprocess.run('docker run --rm -m {}m -v {}:/tmp/extractor -v /dev:/dev --privileged {}'.format(memory_limit, tmpdir.name, container), shell=True)

    logging.warning('Now taking ownership of the files. You may need to enter your password.')

    subprocess.run('sudo chown -R {} {}'.format(os.environ['USER'], tmpdir.name), shell=True)
    with suppress(shutil.Error):
        shutil.copytree(str(Path(tmpdir.name, 'files')), target)

    handle_report(report_file, tmpdir.name)

    tmpdir.cleanup()


def handle_report(report_file, tmp):
    indented_report = json.dumps(json.loads(Path(tmp, 'reports', 'meta.json').read_text()), indent=4)
    if report_file:
        Path(report_file).write_text(indented_report)
    else:
        print(indented_report)


def main():
    arguments = parse_arguments()
    setup_logging(arguments.verbose)

    output_directory = arguments.output_directory if arguments.output_directory else str(Path('.') / 'extracted_files')
    if Path(output_directory).exists():
        logging.error('Target directory exists ({}). Please choose a non-existing directory with -o option.'.format(output_directory))
        return 1

    if not container_exists(arguments.container):
        logging.error('Container {} doesn\'t exist. Please specify an existing container with the -c option.'.format(arguments.container))
        logging.info('You can download the default container with "docker pull {}"'.format(DEFAULT_CONTAINER))
        return 1

    if not Path(arguments.FILE[0]).is_file():
        logging.error('Given input file {} doesn\'t exist. Please give an existing path.'.format(arguments.FILE[0]))
        return 1

    if arguments.report_file and not Path(arguments.report_file).parent.is_dir():
        logging.error('Report file ({}) can not be created. Check if parent directory exists.'.format(arguments.report_file))
        return 1

    if arguments.report_file and Path(arguments.report_file).exists():
        logging.warning('Warning: Report file will be overwritten.')

    call_docker(
        input_file=arguments.FILE[0],
        container=arguments.container,
        target=output_directory,
        report_file=arguments.report_file,
        memory_limit=arguments.memory
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
