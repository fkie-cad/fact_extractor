"""
This plugin unpacks MaxLinear Puma 8 Images.
"""

import os
import struct
from io import BufferedReader
from pathlib import Path

from common_helper_files import write_binary_to_file

NAME = 'MaxLinear Puma 8 Vendor Image'
MIME_PATTERNS = ['firmware/puma-8-vendor-image']
VERSION = '0.1'
UBOOT_HEADER_LEN = 64
UBOOT_IMAGE_HEADER = b'\x27\x05\x19\x56'
FDT_HEADER_LEN = 40
FDT_HEADER = b'\xd0\x0d\xfe\xed'

IMAGE_TYPES = {
    2: 'kernel',
    5: 'firmware',
    7: 'rootfs',
    29: 'fpga',
}

EMPTY_VENDOR_IMAGE = 6


def _seek_component_offset(fp: BufferedReader, component: bytes):
    start = fp.tell()
    header_offset = fp.read().find(component)
    if header_offset != -1:
        fp.seek(start + header_offset)
    else:
        fp.seek(start)


def unpack_function(file_path, tmp_dir):
    file = Path(file_path)

    try:
        with file.open('rb') as f:
            # per the docsis 4.0 spec, all images MUST be signed
            if f.read(2) == b'\x30\x82':
                der_bytes = int.from_bytes(f.read(2), 'big')
                f.seek(0)
                data = f.read(der_bytes + 4)
                write_binary_to_file(data, Path(tmp_dir) / 'signature.der')
            _seek_component_offset(f, UBOOT_IMAGE_HEADER)  # skip the vendor header
            f.read(1)  # jump again so we don't get stuck
            _seek_component_offset(f, UBOOT_IMAGE_HEADER)  # skip multi-file image header
            last_uimage = 0

            while True:
                image_header_data = f.read(UBOOT_HEADER_LEN)
                if not image_header_data or len(image_header_data) != UBOOT_HEADER_LEN:
                    break
                image_header = struct.unpack('>4sIIIIIIBBBB32s', image_header_data)
                image_data_size = image_header[3]
                image_type = image_header[9]
                if image_type == EMPTY_VENDOR_IMAGE:  # ignore empty vendor script
                    f.seek(last_uimage)
                    break
                last_uimage = f.tell()  # save so we can locate dtb before empty vendor script
                data = f.read(image_data_size)
                name = IMAGE_TYPES.get(image_type, 'unknown')
                write_binary_to_file(data, Path(tmp_dir) / name)
                _seek_component_offset(f, UBOOT_IMAGE_HEADER)

            _seek_component_offset(f, FDT_HEADER)
            fdt_header_data = f.read(FDT_HEADER_LEN)
            fdt_header = struct.unpack('>IIIIIIIIII', fdt_header_data)
            fdt_data_size = fdt_header[1]
            f.seek(-FDT_HEADER_LEN, os.SEEK_CUR)  # go back to start of FDT
            data = f.read(fdt_data_size)
            write_binary_to_file(data, Path(tmp_dir) / 'puma8.dtb')

    except OSError as io_error:
        return {'output': f'failed to read file: {io_error!s}'}

    return {'output': 'succesfully unpacked MaxLinear Puma 8 Vendor image'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
