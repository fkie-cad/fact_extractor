"""
This plugin unpacks several formats utilizing patool
"""

from common_helper_process import execute_shell_command

NAME = 'PaTool'
MIME_PATTERNS = [
    'application/java-archive',
    'application/vnd.debian.binary-package',
    'application/vnd.ms-cab-compressed',
    'application/x-ace',
    'application/x-adf',
    'application/x-alzip',
    'application/x-arc',
    'application/x-archive',
    'application/x-bzip2',
    'application/x-cab',
    'application/x-chm',
    'application/x-compress',
    'application/x-cpio',
    'application/x-debian-package',
    'application/x-dms',
    'application/x-lha',
    'application/x-lrzip',
    'application/x-lz4',
    'application/x-lzh',
    'application/x-lzh-compressed',
    'application/x-lzip',
    'application/x-lzo',
    'application/x-lzop',
    'application/x-redhat-package-manager',
    'application/x-rzip',
    'application/x-shar',
    'application/x-tar',
    'application/x-xz',
    'application/x-zoo',
    'application/zpaq',
    'audio/flac',
]
VERSION = '0.6.1'

TOOL_PATH = execute_shell_command('which patool').strip()


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    return {
        'output': execute_shell_command(
            f'fakeroot python3 {TOOL_PATH} extract --outdir {tmp_dir} {file_path}', timeout=600
        )
    }


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
