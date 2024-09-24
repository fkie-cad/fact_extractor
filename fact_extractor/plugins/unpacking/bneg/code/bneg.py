import os
import struct
from pathlib import Path

NAME = 'Instar BNEG'
MIME_PATTERNS = ['firmware/bneg']
VERSION = '0.1.0'
HEADER_SIZE = 20


class BnegHeader:
    def __init__(self, data: bytes):
        (
            self.magic,
            self.major_version,
            self.minor_version,
            *self.partitions,
        ) = struct.unpack('<4sIIII', data)

    def to_dict(self):
        return self.__dict__


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    input_file = Path(file_path)
    output_dir = Path(tmp_dir)
    with input_file.open('rb') as fp:
        header = BnegHeader(fp.read(HEADER_SIZE))
        output = [f'Found BNEG v{header.major_version}.{header.minor_version}']
        offset = HEADER_SIZE
        for idx, partition in enumerate(header.partitions, start=1):
            if partition:
                with (output_dir / f'partition_{idx}.bin').open('wb') as fp_out:
                    os.sendfile(fp_out.fileno(), fp.fileno(), offset, partition)
                output.append(f'Unpacked partition {idx} at offset {offset} to partition_{idx}.bin (size {partition})')
                offset += partition

    return {'output': '\n'.join(output)}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
