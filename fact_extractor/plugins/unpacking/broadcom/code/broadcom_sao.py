"""
This plugin unpacks Broadcom SAO images.
"""

from pathlib import Path

from common_helper_files import write_binary_to_file

NAME = 'Broadcom SAO'
MIME_PATTERNS = ['firmware/broadcom-sao']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir must be used to store the extracted files.
    Optional: Return a dict with meta information
    """

    file = Path(file_path)
    file_size = file.stat().st_size

    try:
        with file.open('rb') as f:
            while f.tell() < file_size:
                f.read(8)  # skip 8 bytes to part name offset
                name = f.read(4).decode('utf-8')
                f.read(4)  # skip 4 more bytes to size offset
                size = int.from_bytes(f.read(4), 'big')
                f.read(44)  # skip rest of header
                data = f.read(size)
                outfile = Path(tmp_dir) / name
                write_binary_to_file(data, outfile)

    except OSError as io_error:
        return {'output': f'failed to read file: {io_error!s}'}

    return {'output': 'successfully unpacked Broadcom SAO image'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
