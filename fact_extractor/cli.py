#!/usr/bin/env python3
"""
Command-line interface for FACT extractor.
Provides unified access to all FACT extractor commands.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from contextlib import suppress
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    __VERSION__ = version('fact-extractor')
except Exception:
    __VERSION__ = '0.0.0'


# === extract-docker logic (integrated from extract.py) ===

DEFAULT_CONTAINER = 'fkiecad/fact_extractor'


def docker_parse_arguments():
    parser = argparse.ArgumentParser(description='Extract using Docker container')
    parser.add_argument('-c', '--container', default=DEFAULT_CONTAINER)
    parser.add_argument('-m', '--memory', default='512', help='memory limit in MB')
    parser.add_argument('-o', '--output_directory', default=None)
    parser.add_argument('-r', '--report_file', default=None)
    parser.add_argument('-V', '--verbose', action='store_true', default=False)
    parser.add_argument('-e', '--extract_everything', action='store_true')
    parser.add_argument('FILE', type=str, nargs=1)
    return parser.parse_args()


def docker_container_exists(container):
    return (
        subprocess.run(
            f'docker history {container}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
        ).returncode
        == 0
    )


def docker_call(input_file, container, target, report_file, memory_limit, extract_everything=False):
    arguments = f'--chown {os.getuid()}:{os.getgid()}'
    arguments += ' --extract_everything' if extract_everything else ''
    tmpdir = TemporaryDirectory()

    try:
        for subpath in ['files', 'reports', 'input']:
            Path(tmpdir.name, subpath).mkdir(exist_ok=True)

        shutil.copy(input_file, str(Path(tmpdir.name, 'input', Path(input_file).name)))

        command = f'docker run --rm --ulimit nofile=20000:50000 -m {memory_limit}m -v {tmpdir.name}:/tmp/extractor -v /dev:/dev --privileged {container} {arguments}'
        subprocess.run(command, shell=True, check=False)

        with suppress(shutil.Error):
            shutil.copytree(str(Path(tmpdir.name, 'files')), target)

        # Handle report
        indented_report = json.dumps(json.loads(Path(tmpdir.name, 'reports', 'meta.json').read_text()), indent=4)
        if report_file:
            Path(report_file).write_text(indented_report)
        else:
            print(indented_report)
    finally:
        tmpdir.cleanup()


def handle_report(report_file, tmp):
    indented_report = json.dumps(json.loads(Path(tmp, 'reports', 'meta.json').read_text()), indent=4)
    if report_file:
        Path(report_file).write_text(indented_report)
    else:
        print(indented_report)


def setup_logging(verbose):
    console_log = logging.StreamHandler()
    console_log.setFormatter(
        logging.Formatter(fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    )

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.addHandler(console_log)


def extract_docker_main():
    args = docker_parse_arguments()

    # Setup logging
    console_log = logging.StreamHandler()
    console_log.setFormatter(
        logging.Formatter(fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    )
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    logger.addHandler(console_log)

    output_directory = args.output_directory if args.output_directory else str(Path() / 'extracted_files')

    if Path(output_directory).exists():
        logging.error(
            f'Target directory exists ({output_directory}). Please choose a non-existing directory with -o option.'
        )
        return 1

    if not docker_container_exists(args.container):
        logging.error(f"Container {args.container} doesn't exist.")
        logging.info(f'You can download the default container with "docker pull {DEFAULT_CONTAINER}"')
        return 1

    if not Path(args.FILE[0]).is_file():
        logging.error(f"Given input file {args.FILE[0]} doesn't exist.")
        return 1

    if args.report_file and not Path(args.report_file).parent.is_dir():
        logging.error(f'Report file ({args.report_file}) can not be created.')
        return 1

    if args.report_file and Path(args.report_file).exists():
        logging.warning('Warning: Report file will be overwritten.')

    docker_call(
        input_file=args.FILE[0],
        container=args.container,
        target=output_directory,
        report_file=args.report_file,
        memory_limit=args.memory,
        extract_everything=args.extract_everything,
    )
    return 0


# === Main CLI ===


def main():
    parser = argparse.ArgumentParser(
        prog='fact-extractor', description='FACT Extractor - Firmware Analysis and Comparison Tool'
    )
    parser.add_argument('--version', action='version', version=f'fact-extractor {__VERSION__}')

    subparsers = parser.add_subparsers(dest='command', required=True)

    # install subcommand
    install_parser = subparsers.add_parser('install', help='Install system dependencies and packages')
    install_parser.add_argument('-d', '--debug', action='store_true', help='print debug messages')

    # extract-docker subcommand
    docker_parser = subparsers.add_parser('extract-docker', help='Extract using Docker container')
    docker_parser.add_argument('-c', '--container', default='fkiecad/fact_extractor')
    docker_parser.add_argument('-m', '--memory', default='512', help='memory limit in MB')
    docker_parser.add_argument('-o', '--output_directory', default=None)
    docker_parser.add_argument('-r', '--report_file', default=None)
    docker_parser.add_argument('-V', '--verbose', action='store_true', default=False)
    docker_parser.add_argument('-e', '--extract_everything', action='store_true')
    docker_parser.add_argument('FILE', type=str, nargs=1)

    # extract-local subcommand
    subparsers.add_parser('extract-local', help='Extract locally without Docker')

    # server subcommand
    server_parser = subparsers.add_parser('server', help='Run extraction server')
    server_parser.add_argument('-b', '--bind', default='0.0.0.0:5000')
    server_parser.add_argument('-w', '--workers', type=int, default=1)
    server_parser.add_argument('-t', '--timeout', type=int, default=600)

    args, unknown = parser.parse_known_args()

    if args.command == 'install':
        sys.argv = ['install'] + unknown
        from fact_extractor.install import main as install_main

        return install_main()

    elif args.command == 'extract-docker':
        sys.argv = ['extract-docker'] + unknown
        return extract_docker_main()

    elif args.command == 'extract-local':
        # fact_extract.main() reads from sys.argv, so we reconstruct it
        sys.argv = ['fact_extract', unknown[0]]  # FILE_PATH is first
        # Parse remaining args for fact_extract
        rest_args = unknown[1:] if len(unknown) > 1 else []
        if rest_args:
            sys.argv.extend(rest_args)
        from fact_extractor.fact_extract import main as extract_main

        return extract_main()

    elif args.command == 'server':
        bind = args.bind
        cmd = ['gunicorn', f'--timeout={args.timeout}', f'-w {args.workers}', f'-b {bind}', 'fact_extractor.server:app']
        return subprocess.call(cmd)


if __name__ == '__main__':
    sys.exit(main())
