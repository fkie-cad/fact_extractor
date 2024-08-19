from __future__ import annotations

import configparser
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import List

from common_helper_process import execute_shell_command_get_return_code


class InstallationError(Exception):
    pass


class OperateInDirectory:
    def __init__(self, target_directory, remove=False):
        self._current_working_dir = None
        self._target_directory = target_directory
        self._remove = remove

    def __enter__(self):
        self._current_working_dir = os.getcwd()
        os.chdir(self._target_directory)

    def __exit__(self, *args):
        os.chdir(self._current_working_dir)
        if self._remove:
            self._remove_folder(self._target_directory)

    @staticmethod
    def _remove_folder(folder_name):
        try:
            shutil.rmtree(folder_name)
        except PermissionError:
            logging.debug(f'Falling back on root permission for deleting {folder_name}')
            execute_shell_command_get_return_code(f'sudo rm -rf {folder_name}')
        except Exception as exception:
            raise InstallationError(exception) from exception


def log_current_packages(packages, install=True):
    action = 'Installing' if install else 'Removing'
    logging.info(f'{action} {" ".join(packages)}')


def run_shell_command_raise_on_return_code(  # pylint: disable=invalid-name
    command: str, error: str, add_output_on_error=False
) -> str:
    output, return_code = execute_shell_command_get_return_code(command)
    if return_code != 0:
        if add_output_on_error:
            error = f'{error}\n{output}'
        raise InstallationError(error)
    return output


def apt_update_sources():
    return run_shell_command_raise_on_return_code(
        'sudo -E apt-get update', 'Unable to update repository sources. Check network.'
    )


def apt_upgrade_system():
    return run_shell_command_raise_on_return_code('sudo -E apt-get upgrade -y', 'Unable to upgrade packages:', True)


def apt_autoremove_packages():
    return run_shell_command_raise_on_return_code(
        'sudo -E apt-get autoremove -y', 'Automatic removal of packages failed:', True
    )


def apt_clean_system():
    return run_shell_command_raise_on_return_code('sudo -E apt-get clean', 'Cleaning of package files failed:', True)


def apt_install_packages(*args):
    if not args:
        return None

    log_current_packages(args)
    return run_shell_command_raise_on_return_code(
        f'sudo -E apt-get install -y {" ".join(args)}', f'Error in installation of package(s) {" ".join(args)}', True
    )


def apt_remove_packages(*args):
    if not args:
        return None

    log_current_packages(args, install=False)
    return run_shell_command_raise_on_return_code(
        f'sudo -E apt-get remove -y {" ".join(args)}', f'Error in removal of package(s) {" ".join(args)}', True
    )


def pip_install_packages(*packages):
    if not packages:
        return

    log_current_packages(packages)
    pip_command = 'pip' if is_virtualenv() else 'sudo -EH pip'
    for packet in packages:
        try:
            run_shell_command_raise_on_return_code(
                f'{pip_command} install --upgrade "{packet}"',
                f'Error in installation of python package {packet}',
                True
            )
        except InstallationError as installation_error:
            if 'is a distutils installed project' in str(installation_error):
                logging.warning(f'Could not update python packet {packet}. Was not installed using pip originally')
            else:
                raise installation_error


def load_requirements_file(path: Path) -> list[str]:
    return [
        line for line in path.read_text().splitlines()
        if line and not line.startswith('#')
    ]


def check_if_command_in_path(command):
    _, return_code = execute_shell_command_get_return_code(f'command -v {command}')
    if return_code != 0:
        return False
    return True


def install_github_project(project_path: str, commands: List[str]):
    log_current_packages([project_path])
    folder_name = Path(project_path).name
    _checkout_github_project(project_path, folder_name)

    with OperateInDirectory(folder_name, remove=True):
        error = None
        for command in commands:
            output, return_code = execute_shell_command_get_return_code(command)
            if return_code != 0:
                error = f'Error while processing github project {project_path}!\n{command}\n{output}'
                break

    if error:
        raise InstallationError(error)


def _checkout_github_project(github_path, folder_name):
    clone_url = f'https://www.github.com/{github_path}'
    stdout, return_code = execute_shell_command_get_return_code(f'git clone {clone_url}')
    if return_code != 0:
        raise InstallationError(f'Cloning from github failed for project {github_path}: {stdout}\n')
    if not Path('.', folder_name).exists():
        raise InstallationError(f'Repository creation failed on folder {folder_name}: {stdout}\n')


def load_main_config():
    config = configparser.ConfigParser()
    config_path = Path(Path(__file__).parent.parent, 'config', 'main.toml')
    if not config_path.is_file():
        raise InstallationError(f'Could not load config at path {config_path}')
    config.read(str(config_path))
    return config


def is_virtualenv() -> bool:
    """Check if FACT runs in a virtual environment"""
    return sys.prefix != getattr(sys, 'base_prefix', getattr(sys, 'real_prefix', None))
