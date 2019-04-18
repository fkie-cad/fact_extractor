
import logging
import re
from os import chdir, getcwd, path, remove, rename

from common_helper_files import get_files_in_dir
from common_helper_process import execute_shell_command_get_return_code
from helperFunctions.file_system import get_src_dir

NAME = 'Ambarella'
MIME_PATTERNS = ['firmware/ambarella']
VERSION = '0.2'


def unpack_function(file_path, tmp_dir):
    script_path = path.join(get_src_dir(), "bin", "amba_fwpak.py")
    if not path.exists(script_path):
        return {'output': "Error: phantom_firmware_tools not installed! Re-Run the installation script!"}

    fallback_directory = getcwd()
    chdir(tmp_dir)

    output, return_code = execute_shell_command_get_return_code('fakeroot {} -x -vv -m {}'.format(script_path, file_path)) + "\n"


    _rename_files(file_path)
    _remove_ini_files()

    chdir(fallback_directory)

    if return_code != 0:
        raise Exception('Non-zero error code {} when executing shell command.'.format(return_code))

    meta_data = {'output': output, 'return_code': return_code}
    logging.debug(output)
    return meta_data


def _rename_files(file_path):
    files = _get_list_of_files()
    basename = path.split(file_path)[1]

    for ini_file, bin_file in files:
        identifier = _get_identifier_from_ini(ini_file)
        rename(bin_file, "{}_{}.partition".format(basename, identifier))


def _get_list_of_files():
    all_files = get_files_in_dir('.')
    bin_files = [any_file for any_file in all_files if any_file.endswith('a9s')]
    files = [('{}a9h'.format(bin_file[:len(bin_file) - 3]), bin_file) for bin_file in bin_files]
    return files


def _get_identifier_from_ini(ini_file):
    identifier = "default"
    with open(ini_file, 'r') as fd:
        lines = fd.readlines()
        for line in lines:
            match = re.match(r"\#.Stores.partition.with.([0-9a-zA-Z ]*)", line)
            if match:
                identifier = match.group(1)
                identifier = identifier.replace(' ', '_')
                identifier = identifier.strip('_')
    return identifier


def _remove_ini_files():
    for file_name in get_files_in_dir('.'):
        if file_name.endswith('.a9h'):
            remove(file_name)


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
