"""
This plugin unpacks several formats that the linux kernel can be compressed with
Implementation logic taken from https://github.com/torvalds/linux/blob/master/scripts/extract-vmlinux
FAQ:
Why not just call this script directly? Well it relies on readelf to determine success, and the readelf on x86 doesn't
read header information of different architectures, eg ARM. So we can do better.
"""

from pathlib import Path
from subprocess import run

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
    'rpmocsser gniuniL...x',  # the same string as 32-bit big endian data blob
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
    return found_cnt > 0


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
    output = ''
    extractor = Extractor(file_path, tmp_dir)
    for compressed_file, command in extractor.get_extracted_files():
        tool = command_absolute_path(command)
        output_file = Path(tmp_dir) / compressed_file.with_suffix('').name

        cmd = f'fakeroot cat {compressed_file} | {tool} > {output_file}'
        output += cmd + '\n'
        proc = run(cmd, shell=True, check=False, timeout=600, capture_output=True)
        output += proc.stdout.decode(errors='replace')
        # remove the compressed file
        compressed_file.unlink()

        if proc.returncode != 0 and b'decompression OK' not in proc.stderr:
            output += f"return code: {proc.returncode}: {proc.stderr.decode(errors='replace')}"

        if not output_file.is_file():
            continue
        if not is_kernel(output_file):
            output_file.unlink()
            continue
        output += f'Found Kernel {output_file}\n'
        cmd = f'fakeroot {VMLINUX_TO_ELF_PATH} {output_file} {output_file.with_suffix(".elf")}'
        output += cmd + '\n'
        output += execute_shell_command(cmd, timeout=600)

    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
