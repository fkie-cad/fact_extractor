"""
This plugin unpacks Intel (MaxLinear) UImages.

Reference code: https://bitbucket.org/fesc2000/uimg-tool/src/master/
The above code never successfully unpacked an image for me, though the header
structure was correct.
"""

import struct
from io import BufferedReader
from pathlib import Path

from common_helper_files import write_binary_to_file

NAME = 'MaxLinear UImage'
MIME_PATTERNS = ['firmware/maxlinear-uimage-v2', 'firmware/maxlinear-uimage-v3']
VERSION = '0.1'

HEADER_V2 = 2
HEADER_V3 = 3


def _seek_header_offset(fp: BufferedReader):
    fp.seek(0)
    header_offset = fp.read().find(b'VER2')
    if header_offset != -1:
        fp.seek(header_offset)
        return HEADER_V2
    fp.seek(0)
    header_offset = fp.read().find(b'VER3')
    if header_offset != -1:
        fp.seek(header_offset)
        return HEADER_V3
    return 0


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir must be used to store the extracted files.
    Optional: Return a dict with meta information
    """

    file = Path(file_path)
    header_layout_v2 = '> I 20s I I I I I I I 40s 40s 10s 10s 8s'
    header_layout_v3 = '> I 20s I I I I I I I 80s 80s 20s 20s'

    components = {
        2: 'atomkernel.img',
        3: 'atomrootfs.hsqs',
        8: 'armkernel.img',
        9: 'armrootfs.hsqs',
        10: 'gwrootfs.bin',
    }

    try:
        with file.open('rb') as f:
            # check if image is signed
            if f.read(2) == b'\x30\x82':
                der_bytes = int.from_bytes(f.read(2), 'big')
                f.seek(0)
                data = f.read(der_bytes)
                write_binary_to_file(data, Path(tmp_dir) / 'signature.der')

            # get UImage
            version = _seek_header_offset(f)
            if version == HEADER_V2:
                header_struct = struct.Struct(header_layout_v2)
            elif version == HEADER_V3:
                header_struct = struct.Struct(header_layout_v3)
            else:
                raise ValueError(f'unsupported header version {version}')
            header = header_struct.unpack(f.read(header_struct.size))
            num_parts = header[6]  # number of components
            for i in range(num_parts):
                part_size = int.from_bytes(header[10][(4 * i) : 4 + (4 * i)], 'big')
                part_type = int.from_bytes(header[11][i : i + 1], 'big')
                name = components.get(part_type, f'unkonwn-{i!s}')
                data = f.read(part_size)
                write_binary_to_file(data, Path(tmp_dir) / name)

    except OSError as io_error:
        return {'output': f'failed to read file: {io_error!s}'}

    except struct.error as struct_error:
        return {'output': f'failed to unpack header: {struct_error!s}'}

    return {'output': 'successfully unpacked MaxLinear Puma 7 image'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
