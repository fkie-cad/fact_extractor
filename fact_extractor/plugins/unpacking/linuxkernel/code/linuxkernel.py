"""
This plugin unpacks several formats that the linux kernel can be compressed with
Implementation logic taken from https://github.com/torvalds/linux/blob/master/scripts/extract-vmlinux
FAQ:
Why not just call this script directly? Well it relies on readelf to determine success, and the readelf on x86 doesn't
read header information of different architectures, eg ARM. So we can do better.
"""

from pathlib import Path

from common_helper_process import execute_shell_command, execute_shell_command_get_return_code

from plugins.unpacking.linuxkernel.internal.extractor import Extractor

NAME = 'LinuxKernel'
MIME_PATTERNS = ['linux/kernel']
VERSION = '0.0.1'

STRINGS_PATH = execute_shell_command('which strings').strip()
VMLINUX_TO_ELF_PATH = execute_shell_command('which vmlinux-to-elf').strip()
TOOL_PATHS = {}
KERNEL_STRINGS_TO_MATCH = [
    'Linux version',
    'jiffies',
    'syscall',
    'This kernel requires',
    'Uncompressing Linux...',
    'rpmocsser gniuniL...x',  # the same string as 32 bit big endian data blob
]


def is_kernel(file_path):
    """
    fairly mundane checks for strings that should occur in any linux kernel
    """
    found_cnt = 0
    for i in KERNEL_STRINGS_TO_MATCH:
        output, ret_code = execute_shell_command_get_return_code(f'{STRINGS_PATH} {file_path} | grep -q "{i}"')
        if ret_code == 0:
            found_cnt += 1

    # if any two or more criteria match, then we found what is likely a kernel
    return found_cnt > 0


def check_dir_for_extracted_kernel(tmp_dir):
    """
    loop through the tmp_dir, find all files and check if any of them are a kernel
    remove files that aren't valid kernels.
    """
    files_in_dir = [f for f in Path(tmp_dir).iterdir() if f.is_file()]
    found = False
    for file in files_in_dir:
        if is_kernel(file):
            found = True
        else:
            file.unlink()

    return found


def command_absolute_path(cmd):
    """
    we want to use the absolute path for a tool so we can execute in fakeroot
    """
    tool = cmd[0]
    if tool not in TOOL_PATHS:
        TOOL_PATHS[tool] = execute_shell_command(f'which {tool}').strip()
    cmd[0] = TOOL_PATHS[tool]
    return ' '.join(cmd)


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    output, output_file_name = '', None
    extractor = Extractor(file_path, tmp_dir)
    for file_data in extractor.extracted_files():
        compressed_file = file_data['file_path']
        tool = command_absolute_path(file_data['command'])
        output_file_name = compressed_file.with_suffix('')

        cmd = f'fakeroot cat {compressed_file} | {tool} > {Path(tmp_dir, output_file_name)} 2> /dev/null'
        output += cmd + '\n'
        output += execute_shell_command(cmd, timeout=600)

        # remove the compressed file
        Path(file_data['file_path']).unlink()

        found = check_dir_for_extracted_kernel(tmp_dir)
        if found:
            output += f'Found Kernel {output_file_name}\n'
            break

    # The resulting output could be a variety of formats, what we want to do is rebuild it as a non-stripped ELF
    # that is then easily analyzable in your favorite tools. Use vmlinux-to-elf for this.
    if output_file_name:
        cmd = f'fakeroot {VMLINUX_TO_ELF_PATH} {output_file_name} {output_file_name}.elf'
        output += cmd + '\n'
        output += execute_shell_command(cmd, timeout=600)

    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
