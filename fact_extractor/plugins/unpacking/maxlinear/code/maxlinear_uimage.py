"""
This plugin unpacks Intel (MaxLinear) UImages.
"""

import struct

from io import BufferedReader
from pathlib import Path

from common_helper_files import write_binary_to_file

NAME = "MaxLinear UImage"
MIME_PATTERNS = ['firmware/maxlinear-uimage-v2', 'firmware/maxlinear-uimage-v3']
VERSION = '0.1'

def _seek_header_offset(fp: BufferedReader):
    fp.seek(0)
    header_offset = fp.read().find(b'VER2')
    if header_offset != -1:
        fp.seek(header_offset)
        return 2
    fp.seek(0)
    header_offset = fp.read().find(b'VER3')
    if header_offset != -1:
        fp.seek(header_offset)
        return 3

def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir must be used to store the extracted files.
    Optional: Return a dict with meta information
    """

    file = Path(file_path)
    HEADER_LAYOUT_V2 = '> I 20s I I I I I I I 40s 40s 10s 10s 8s'
    HEADER_LAYOUT_V3 = '> I 20s I I I I I I I 80s 80s 20s 20s'

    components = {
        2: "atomkernel.img",
        3: "atomrootfs.hsqs",
        8: "armkernel.img",
        9: "armrootfs.hsqs",
        10: "gwrootfs.bin"
    }

    try:
        with file.open('rb') as f:
            # check if image is signed
            if (f.read(2) == b'\x30\x82'):
                der_bytes = int.from_bytes(f.read(2), 'big')
                f.seek(0)
                data = f.read(der_bytes)
                write_binary_to_file(data, Path(tmp_dir) / 'signature.der')

            # get UImage
            version = _seek_header_offset(f)
            if version == 2:
                HEADER = struct.Struct(HEADER_LAYOUT_V2)
            elif version == 3:
                HEADER = struct.Struct(HEADER_LAYOUT_V3)
            header = HEADER.unpack(f.read(HEADER.size))
            num_parts = header[6] # number of components
            for i in range(num_parts):
                part_size = int.from_bytes(header[10][(4 * i):4 + (4 * i)], 'big')
                part_type = int.from_bytes(header[11][i:i + 1], 'big')
                name = components.get(part_type)
                data = f.read(part_size)
                if (name):
                    write_binary_to_file(data, Path(tmp_dir) / name)
                else:
                    name = 'unknown-' + str(i)
                    write_binary_to_file(data, Path(tmp_dir) / name)

    except OSError as io_error:
        return {'output': f'failed to read file: {io_error!s}'}
    
    return {'output': 'successfully unpacked MaxLinear Puma 7 image'}

# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
