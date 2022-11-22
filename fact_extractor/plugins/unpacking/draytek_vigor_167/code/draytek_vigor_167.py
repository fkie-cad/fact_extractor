'''
This plugin extracts the squashfs root filesystem in Draytek Vigor 167 firmware containers.
'''
import struct
from pathlib import Path
from common_helper_files import write_binary_to_file

NAME = 'Draytek Vigor 167'
MIME_PATTERNS = ['firmware/draytek-vigor-167']
VERSION = '0.1'

HEADER_LAYOUT = '> 4s I I I 64x I I 49x I I 117x'
HEADER = struct.Struct(HEADER_LAYOUT)


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir must be used to store the extracted files.
    Optional: Return a dict with meta information
    '''
    with open(file_path, 'rb') as f:
        signature = HEADER.unpack(f.read(HEADER.size))
        f.seek(signature[1] + signature[4])
        squashfs = f.read(signature[5])

    output_file_path = Path(tmp_dir) / 'squashfs_root'
    write_binary_to_file(squashfs, output_file_path)
    return {'output': 'successfully unpacked image'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
