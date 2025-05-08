import string
import struct
from pathlib import Path

PRINTABLE_CHARS = set(string.printable.encode())

NAME = 'gm8126'
MIME_PATTERNS = ['firmware/gm8126']
VERSION = '0.1.0'
HEADER_SIZE = 0x100


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    extraction_dir = Path(tmp_dir)
    input_file = Path(file_path)
    output_file = extraction_dir / 'kernel.img'
    with input_file.open('rb') as fp_in, output_file.open('wb') as fp_out:
        fp_in.seek(8)
        file_size = struct.unpack('>I', fp_in.read(4))[0]
        fp_in.seek(HEADER_SIZE)
        fp_out.write(fp_in.read(file_size))
    return {'output': f'Successfully unpacked {input_file.name} to "kernel.img" (size: {file_size} bytes)'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
