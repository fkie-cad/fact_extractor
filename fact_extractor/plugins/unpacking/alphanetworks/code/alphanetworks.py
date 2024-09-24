import string
from base64 import b64decode
from pathlib import Path

PRINTABLE_CHARS = set(string.printable.encode())

NAME = 'alphanetworks'
MIME_PATTERNS = ['firmware/alphanetworks']
VERSION = '0.1.0'

FW_BOUNDARY_STR = b'=== Firmware Boundary ===\n'
DDPACK_BOUNDARY_STR = b'=== ddPack Boundary ===\n'
BASE64_STR = b'begin-base64\n'


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    extraction_dir = Path(tmp_dir)
    contents = Path(file_path).read_bytes()
    script_end, base64_start = None, None

    ddpack_offset = contents.find(DDPACK_BOUNDARY_STR)
    if ddpack_offset != -1:
        script_end = ddpack_offset
        ddpack_offset += len(DDPACK_BOUNDARY_STR)

        base64_string_index = contents.find(b'begin-base64')
        if base64_string_index != -1:
            base64_start = base64_string_index + contents[base64_string_index:].find(b'\n') + 1
            # after the base64 block there is a line with "===="
            base64_end = base64_start + contents[base64_start:].find(b'\n====\n')
            # add some padding at the end in case it is missing
            elf_content = b64decode(contents[base64_start:base64_end] + b'===')
            elf_file = extraction_dir / 'ddPack.elf'
            elf_file.write_bytes(elf_content)

    fw_offset = contents.find(FW_BOUNDARY_STR)
    if script_end is None:
        script_end = fw_offset
    fw_offset += len(FW_BOUNDARY_STR)

    script = contents[:script_end]
    script_file = extraction_dir / 'script.sh'
    script_file.write_bytes(script)

    fw_content = contents[fw_offset:]
    # for whatever reason, the samples beginning with "REDSONIC" are bit-wise inverted, so we
    # undo that before saving the firmware image to file
    inverted = _fw_is_inverted(fw_content)
    if inverted:
        fw_content = _invert_bytes(fw_content)

    fw_file = extraction_dir / 'firmware.bin'
    fw_file.write_bytes(fw_content)

    return {
        'output': {
            'firmware offset': fw_offset,
            'ddpack offset': ddpack_offset if ddpack_offset != -1 else None,
            'base64 offset': base64_start,
            'inverted': inverted,
        }
    }


def _fw_header_contains_name(file_name: bytes) -> bool:
    return file_name and all(c in PRINTABLE_CHARS for c in file_name)


def _fw_is_inverted(fw_content: bytes) -> bool:
    return fw_content.startswith(_invert_bytes(b'REDSONIC'))


def _invert_bytes(byte_str: bytes) -> bytes:
    return bytes([c ^ 0xFF for c in byte_str])


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
