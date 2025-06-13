"""
This plugin unpacks several formats utilizing patool
"""

from helperFunctions.process import run_command

NAME = 'PaTool'
MIME_PATTERNS = [
    'application/bzip3',
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
    'application/zstd',
    'audio/flac',
]
VERSION = '0.7.0'

TOOL_PATH = run_command('which patool')


def unpack_function(file_path: str, tmp_dir: str):
    return {
        'output': run_command(f'fakeroot python3 {TOOL_PATH} extract --outdir {tmp_dir} {file_path}'),
    }


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
