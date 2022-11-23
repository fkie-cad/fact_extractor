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
# ┌─Draytek Vigor 167 - firmware container (big endian)─┐
# │  4 bytes    // Magic field, expected '2RHD'         │
# │  uint32     // Header size, expected 256 bytes      │
# │  uint32     // File size without footer             │
# │  uint32     // CRC32 checksum                       │
# │  64 bytes   // First padding                        │
# │  uint32     // Kernel blob size                     │
# │  uint32     // Squashfs blob size                   │
# │  49 bytes   // Second padding                       │
# │  uint8      // First unknown                        │
# │  uint8      // Second unknown                       │
# │  117 bytes  // Third padding                        │
# └─────────────────────────────────────────────────────┘


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir must be used to store the extracted files.
    Optional: Return a dict with meta information
    '''
    try:
        with open(file_path, 'rb') as f:
            signature = HEADER.unpack(f.read(HEADER.size))
            f.seek(signature[1] + signature[4])
            squashfs = f.read(signature[5])
    except IOError as io_error:
        return {'output': 'failed to read file: {}'.format(str(io_error))}
    except struct.error as struct_error:
        return {'output': 'failed to extract header: {}'.format(str(struct_error))}

    output_file_path = Path(tmp_dir) / 'squashfs_root'
    write_binary_to_file(squashfs, output_file_path)
    return {
        'output': 'successfully unpacked image',
        'file_header': {
            'magic_field': signature[0],
            'header_size': signature[1],
            'file_size': signature[2],
            'crc32': signature[3],
            'kernel_size': signature[4],
            'squashfs_size': signature[5]
        },
    }


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
