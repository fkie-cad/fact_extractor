import struct
from contextlib import suppress
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict

from common_helper_process import execute_shell_command

NAME = 'BoschFirmwareTool'
MIME_PATTERNS = ['firmware/bosch']
VERSION = '0.1'

TOOL_PATH = Path(__file__).parent.parent / 'bin' / 'boschfwtool'


class FirmwareHeader:  # pylint: disable=too-many-instance-attributes
    header_length = 0x400
    magic_string = b"\x10\x12\x20\x03"

    def __init__(self, file_content: bytes, offset: int = 0, is_subheader: bool = False):
        self.file_content = file_content
        self.is_subheader = is_subheader
        self.offset = offset
        header_content = file_content[offset:]
        self.magic = header_content[0:4]
        self.target = header_content[4:8]
        self.variant = header_content[8:12]
        self.version = struct.unpack('>4b', header_content[12:16])
        self.length = struct.unpack('>i', header_content[16:20])[0]
        self.base = header_content[20:24]
        self.checksum = header_content[24:28]
        self.type = struct.unpack('>i', header_content[28:32])[0]
        self.signature = header_content[76:332]
        self.key_blob = header_content[588:844]

    def __str__(self):
        header_prefix = 'Sub-' if self.is_subheader else ''
        output = [f'Firmware {header_prefix}Header at offset {self.offset}:']
        for attribute in ['magic', 'target', 'variant', 'version', 'length', 'base', 'checksum', 'type', 'signature', 'key_blob']:
            value = getattr(self, attribute)
            value = f'0x{value.hex()}' if isinstance(value, bytes) else str(value)
            output.append(f'{attribute}: {value}')
        return '\n'.join(output)

    def next_header_exists(self, next_offset):
        return (
            next_offset > self.offset
            and len(self.file_content) >= next_offset + self.header_length
            and self._magic_matches(next_offset)
        )

    def _magic_matches(self, offset):
        return self.file_content[offset:offset + 4] == self.magic_string


class FirmwareHeaderIterator:
    def __init__(self, file_content: bytes):
        self.header = FirmwareHeader(file_content)
        self.first_iteration = True

    def __iter__(self):
        return self

    def __next__(self):
        if self.first_iteration:
            self.first_iteration = False
            return self.header
        next_header_offset = self.header.offset + self.header.header_length + (self.header.length if self.header.is_subheader else 0)
        if self.header.next_header_exists(next_header_offset):
            with suppress(KeyError, IndexError, struct.error):
                self.header = FirmwareHeader(self.header.file_content, offset=next_header_offset, is_subheader=True)
                return self.header
        raise StopIteration


def get_header_info(file_path: str) -> str:
    content = Path(file_path).read_bytes()
    return '\n'.join([str(header) for header in FirmwareHeaderIterator(content)])


def unpack_function(file_path: str, tmp_dir: TemporaryDirectory) -> Dict[str, str]:
    """
    Extract Bosch .fw files
    Source: https://github.com/anvilventures/BoschFirmwareTool
    """
    command = f'{TOOL_PATH} {file_path} -o {tmp_dir}'
    output = execute_shell_command(command, timeout=30)
    try:
        header_info = get_header_info(file_path)
    except IndexError:
        header_info = 'Error during header parsing'

    return {'output': output, 'header': header_info}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
