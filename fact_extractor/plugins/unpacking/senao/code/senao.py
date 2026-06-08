from __future__ import annotations

import struct
from pathlib import Path
from typing import Iterable

NAME = 'senao'
MIME_PATTERNS = [
    'firmware/senao-v1a',
    'firmware/senao-v1b',
    'firmware/senao-v2a',
    'firmware/senao-v2b',
    'firmware/senao-v2c',
]
VERSION = '0.2.0'

SENAO_V1_MAGIC = bytes.fromhex('12 34 56 78')
SENAO_V2_MAGIC = bytes.fromhex('30 47 16 88')
SENAO_V1_KEY = 0x5678
SENAO_V2_KEY = 0x1688
V2_VERSION_STR = b'3047'


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    extraction_dir = Path(tmp_dir)
    in_file = Path(file_path)
    contents = in_file.read_bytes()
    key, payload_offset = _find_key_and_offset(contents)

    output_file = extraction_dir / f'{in_file.name}.decrypted'
    output_file.write_bytes(bytes(_decrypt_payload(contents[payload_offset:], key)))

    return {
        'output': f'Found payload at offset {payload_offset}.\nDecrypted with key 0x{key:x}.',
    }


def _find_key_and_offset(contents: bytes) -> tuple[int, int]:
    if contents[92:96] == SENAO_V1_MAGIC:
        key = SENAO_V1_KEY
        if contents[96:99] == b'all':  # firmware/senao-v1a (long header variant)
            # this variant has a variable header length (because of a variable length string field)
            # the length of this variable length field is stored as uint32 (be) at offset 0x84
            model_name_len = struct.unpack('>I', contents[0x84 : 0x84 + 4])[0]
            payload_offset = 0x88 + model_name_len
        else:  # firmware/senao-v1b (short header variant)
            payload_offset = 0x60
    else:
        key = SENAO_V2_KEY
        if contents[0xB4 : 0xB4 + 4] == SENAO_V2_MAGIC:  # firmware/senao-v2a (long header variant)
            payload_offset = 0xB8
        elif contents[0x7C : 0x7C + 4] == SENAO_V2_MAGIC:  # firmware/senao-v2b (short header variant)
            payload_offset = 0x80
        elif contents[0x11C : 0x11C + 4] == SENAO_V2_MAGIC:  # firmware/senao-v2c (very long header variant)
            payload_offset = 0x120
        elif contents[0x66 : 0x66 + 4] == V2_VERSION_STR:  # firmware/senao-v2a with different key
            key = int.from_bytes(contents[0xB4 : 0xB4 + 4], byteorder='big')
            payload_offset = 0xB8
        elif contents[0x7C : 0x7C + 4] == V2_VERSION_STR:  # firmware/senao-v2b with different key
            key = int.from_bytes(contents[0xB4 : 0xB4 + 4], byteorder='big')
            payload_offset = 0x80
        elif contents[0xCE : 0xCE + 4] == V2_VERSION_STR:  # firmware/senao-v2c with different key
            key = int.from_bytes(contents[0x11C : 0x11C + 4], byteorder='big')
            payload_offset = 0x120
        else:
            raise ValueError('Invalid input data.')  # The signature should make sure that this does not happen
    return key, payload_offset


def _decrypt_payload(payload: bytes, key: int) -> Iterable[int]:
    for i, char in enumerate(payload):
        yield char ^ (key >> (i % 8)) & 0xFF


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
