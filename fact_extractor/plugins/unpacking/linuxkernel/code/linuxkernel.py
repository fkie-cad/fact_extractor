'''
This plugin unpacks several formats that the linux kernel can be compressed with
Implementation logic taken from https://github.com/torvalds/linux/blob/master/scripts/extract-vmlinux
FAQ:
 Why not just call this script directly? Well it relies on readelf to determine success, and the readelf on x86 doesn't read
header information of different architectures, eg ARM. So we can do better.
'''
import os
import sys
from os import listdir
from os.path import isfile, join
from pathlib import Path

from common_helper_process import execute_shell_command, execute_shell_command_get_return_code

INTERNAL_DIR = Path(__file__).parent.parent / 'internal'
sys.path.append(str(INTERNAL_DIR))
from extractor import Extractor  # noqa: E402 pylint: disable=import-error,wrong-import-position

NAME = 'LinuxKernel'
MIME_PATTERNS = [
    'linux/kernel'
]
VERSION = '0.0.1'

STRINGS_PATH = execute_shell_command('which strings').strip()
TOOL_PATHS = {}
KERNEL_STRINGS_TO_MATCH = ['Linux version', 'jiffies', 'syscall']


def is_kernel(file_path):
    """
    fairly mundane checks for strings that should occur in any linux kernel
    """
    found_cnt = 0
    for i in KERNEL_STRINGS_TO_MATCH:
        output, ret_code = execute_shell_command_get_return_code(
            '{} {}|grep -q "{}"'.format(STRINGS_PATH, file_path, i))
        if 0 == ret_code:
            found_cnt += 1

    # if any two or more criteria match, then we found what is likely a kernel
    return found_cnt > 1


def check_dir_for_extracted_kernel(tmp_dir):
    """
    loop through the tmp_dir, find all files and check if any of them are a kernel
    remove files that aren't valid kernels.
    """
    files_in_dir = [join(tmp_dir, f) for f in listdir(tmp_dir) if isfile(join(tmp_dir, f))]
    found = False
    for file in files_in_dir:
        if is_kernel(file):
            found = True
        else:
            os.remove(file)

    return found


def command_absolute_path(cmd):
    """
    we want to use the absolute path for a tool so we can execute in fakeroot
    """
    tool = cmd[0]
    if tool not in TOOL_PATHS:
        TOOL_PATHS[tool] = execute_shell_command('which {}'.format(tool)).strip()
    cmd[0] = TOOL_PATHS[tool]
    return ' '.join(cmd)


def strip_extension(filename):
    return filename[:filename.rfind('.')]


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    output = ''
    extractor = Extractor(file_path, tmp_dir)
    print('*' * 80)
    for file_data in extractor.extracted_files():
        print('?' * 80)
        compressed_file = file_data['file_path']
        tool = command_absolute_path(file_data['command'])
        output_file_name = strip_extension(compressed_file)

        cmd = 'fakeroot cat {compressed_file} | {tool} > {output_file} 2> /dev/null'.format(
            compressed_file=compressed_file,
            tool=tool, output_file=os.path.join(tmp_dir, output_file_name))
        output += cmd + '\n'
        output += execute_shell_command(cmd, timeout=600)

        # remove the compressed file
        os.remove(file_data['file_path'])

        found = check_dir_for_extracted_kernel(tmp_dir)
        if found:
            break

    return {
        'output': output
    }


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
