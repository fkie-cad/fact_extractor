"""
This plugin extracts the squashfs root filesystem in Draytek Vigor 167 firmware containers.
"""

import struct
from pathlib import Path

from common_helper_files import write_binary_to_file

NAME = 'Draytek Vigor 167'
MIME_PATTERNS = ['firmware/draytek-vigor-167']
VERSION = '0.2'

HEADER_LAYOUT = '> 4s I I I 64x I I 49x b b 117x'
HEADER = struct.Struct(HEADER_LAYOUT)

FOOTER_LAYOUT = '> 16s 33s'
FOOTER = struct.Struct(FOOTER_LAYOUT)

# ┌─Draytek Vigor 167 - firmware container (big endian)─────────┐
# │  4 bytes    // Magic field, expected '2RHD'                 │
# │  uint32     // Header size, expected 256 bytes              │
# │  uint32     // File size without footer                     │
# │  uint32     // CRC32 checksum                               │
# │  64 bytes   // First padding                                │
# │  uint32     // Kernel blob size                             │
# │  uint32     // Squashfs blob size                           │
# │  49 bytes   // Second padding                               │
# │  uint8      // First unknown                                │
# │  uint8      // Second unknown                               │
# │  117 bytes  // Third padding                                │
# │  <x> bytes  // kernel image                                 │
# │  <x> bytes  // squashfs image                               │
# │  16 bytes   // Magic field, expected 'DrayTekImageMD5\n'    │
# │  33 bytes   // Hex-encoded MD5 checksum (null-terminated)   │
# └─────────────────────────────────────────────────────────────┘


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir must be used to store the extracted files.
    Optional: Return a dict with meta information
    """
    try:
        with open(file_path, 'rb') as f:
            signature = HEADER.unpack(f.read(HEADER.size))
            kernel_image = f.read(signature[4])
            squashfs = f.read(signature[5])
            footer = FOOTER.unpack(f.read(FOOTER.size))
    except OSError as io_error:
        return {'output': f'failed to read file: {io_error!s}'}
    except struct.error as struct_error:
        return {'output': f'failed to recognize firmware container: {struct_error!s}'}

    output_file_path_kernel = Path(tmp_dir) / 'kernel_image'
    write_binary_to_file(kernel_image, output_file_path_kernel)

    output_file_path_squashfs = Path(tmp_dir) / 'squashfs_root'
    write_binary_to_file(squashfs, output_file_path_squashfs)

    return {
        'output': 'successfully unpacked image',
        'file_header': {
            'magic_field_header': signature[0],
            'header_size': signature[1],
            'file_size': signature[2],
            'crc32': signature[3],
            'kernel_size': signature[4],
            'squashfs_size': signature[5],
            'magic_field_footer': footer[0],
            'md5_checksum': footer[1],
        },
    }


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
