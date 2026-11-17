"""
This plugin unpacks Starlink User Terminal sxverity images.

sxverity is SpaceX's custom wrapper around the dm-verity kernel feature used
to authenticate firmware partitions and software update bundles. An image
consists of a 0x1000 byte header (four 0x400 byte copies, each possibly signed
with a different key), followed by a romfs payload and a trailing verity hash
tree (32 byte hashes over 1024 byte payload blocks).

See https://blog.quarkslab.com/starlink.html
"""

import struct
from pathlib import Path

from common_helper_files import write_binary_to_file

NAME = 'Starlink sxverity Image'
MIME_PATTERNS = ['firmware/starlink-sxverity']
VERSION = '0.1'

SXVERITY_MAGIC = b'sxverity'
SXVERITY_HEADER_LEN = 0x1000
PAYLOAD_SIZE_OFFSET = 0x0C
ROMFS_MAGIC = b'-rom1fs-'


def unpack_function(file_path, tmp_dir):
    file = Path(file_path)
    try:
        data = file.read_bytes()
    except OSError as io_error:
        return {'output': f'failed to read file: {io_error!s}'}

    if not data.startswith(SXVERITY_MAGIC):
        return {'output': 'missing sxverity magic'}

    # payload size is stored as little-endian u32 at 0x0C of each header copy
    (payload_size,) = struct.unpack_from('<I', data, PAYLOAD_SIZE_OFFSET)
    romfs_end = SXVERITY_HEADER_LEN + payload_size
    if not data.startswith(ROMFS_MAGIC, SXVERITY_HEADER_LEN) or romfs_end > len(data):
        return {'output': 'invalid sxverity image: no romfs payload found behind header'}

    write_binary_to_file(data[:SXVERITY_HEADER_LEN], Path(tmp_dir) / 'sxverity')
    write_binary_to_file(data[SXVERITY_HEADER_LEN:romfs_end], Path(tmp_dir) / 'romfs')

    output = 'successfully unpacked sxverity header and romfs'
    hash_tree = data[romfs_end:]
    if hash_tree.strip(b'\0'):
        # everything behind the romfs is the verity hash tree covering the payload
        write_binary_to_file(hash_tree, Path(tmp_dir) / 'hash_tree')
        output += ' and verity hash tree'

    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
