import struct
from pathlib import Path
from typing import List

NAME = 'ROSFile'
MIME_PATTERNS = ['firmware/ros']
VERSION = '0.8'

MAXIMUM_PART_NUMBER = 100
HEADER_VERSIONS_AND_SIZES = {b'1.01': 48, b'2.00': 80}


def infer_endianness_from_file_count(header: bytes) -> str:
    return '<' if struct.unpack('<I', header[0x20:0x24])[0] < MAXIMUM_PART_NUMBER else '>'


def infer_header_size_from_version(header: bytes) -> int:
    for version, size in HEADER_VERSIONS_AND_SIZES.items():
        if header[0x04:0x08] == version:
            return size
    raise ValueError(f'Unknown ros header version {header[0x04:0x08]}')


def calculate_file_count(header: bytes, endianness: str) -> int:
    return struct.unpack(f'{endianness}I', header[0x20:0x24])[0]


def generate_part_information(header: bytes, endianness: str, number_of_files: int) -> List[dict]:
    parts = []
    header_size = infer_header_size_from_version(header)

    for index in range(number_of_files):
        offset = header_size + index * 32
        parts.append(
            {
                'index': index,
                'file_name': header[offset : offset + 16].decode().strip('\x00'),
                'offset': struct.unpack(f'{endianness}i', header[offset + 16 : offset + 20])[0],
            }
        )
    return parts


def is_last_part(index: int, number_of_parts: int) -> bool:
    return index == number_of_parts - 1


def calculate_part_sizes(rosfile: Path, parts: List[dict]):
    for part in parts:
        if is_last_part(part['index'], len(parts)):
            part['size'] = rosfile.stat().st_size - part['offset']
        else:
            part['size'] = parts[part['index'] + 1]['offset'] - part['offset']


def store_parts_in_tmp_dir(file_path: str, parts: List[dict], tmp_dir: str):
    with open(file_path, 'rb') as ros_fd:
        for part in parts:
            part_file = Path(tmp_dir, part['file_name'])
            ros_fd.seek(part['offset'])
            part_file.write_bytes(ros_fd.read(part['size']))


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    with open(file_path, 'rb') as fd:
        header = fd.read(512)

    endianness = infer_endianness_from_file_count(header)
    number_of_files = calculate_file_count(header, endianness)

    try:
        parts = generate_part_information(header, endianness, number_of_files)
    except ValueError as value_error:
        return {'error': str(value_error)}

    parts.sort(key=lambda x: x['index'])
    calculate_part_sizes(Path(file_path), parts)
    store_parts_in_tmp_dir(file_path, parts, tmp_dir)

    return {
        'file_information': parts,
        'endianness': 'le' if endianness == '<' else 'be',
        'ros_header_version': header[0x04:0x08].decode(),
    }


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
