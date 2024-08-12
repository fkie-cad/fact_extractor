import struct
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

NAME = 'tenvis_pk2'
MIME_PATTERNS = ['firmware/pk2']
VERSION = '0.1.0'

PK2_MAGIC = b'PK2\x00'
XOR_KEY = [0xA1, 0x83, 0x24, 0x78, 0xB3, 0x41, 0x43, 0x56]
KEY_LEN = len(XOR_KEY)


class Pk2FileHeader:
    """
    Header struct:
     0 | 4 | uint32 magic
     4 | 4 | uint32 camera type
     8 | 4 | uint32 creation time
    12 | 4 | char[4] version
    16 | 8 | char[8] reserved
    24 | 4 | uint32 section count
    total size: 28 bytes
    """

    size = 28

    def __init__(self, fp: BinaryIO):
        file_hdr_data = fp.read(self.size)
        self.magic = file_hdr_data[:4]  # we parse the magic as bytes
        self.camera_type, self.creation_time = struct.unpack('<II', file_hdr_data[4:12])
        self.creation_time_readable = datetime.fromtimestamp(self.creation_time).isoformat()
        self.version = file_hdr_data[12:16]
        self.reserved = file_hdr_data[16:24]
        self.section_count = struct.unpack('<I', file_hdr_data[24:28])[0]

    def to_dict(self):
        return {
            'magic': self.magic.decode(errors='replace'),
            'camera_type': self.camera_type,
            'creation_time': self.creation_time_readable,
            'version': self.version.rstrip(b'\x00').decode('ascii', errors='replace'),
            'reserved': self.reserved.rstrip(b'\x00').decode('ascii', errors='replace'),
            'section_count': self.section_count,
        }


class Pk2SectionHeader:
    """
     0 |  4 | uint32 section type
     4 | 16 | char[16] hash
    20 |  4 | uint32 payload size
    total size: 24 bytes
    """

    size = 24

    def __init__(self, fp: BinaryIO, offset: int):
        fp.seek(offset)
        section_header_data = fp.read(self.size)
        self.offset = offset
        self.type = section_header_data[:4].rstrip(b'\x00').decode('ascii', errors='replace')
        self.hash = section_header_data[4:20].hex()
        self.payload_size = struct.unpack('<I', section_header_data[20:24])[0]

    def to_dict(self):
        return self.__dict__


class Pk2File:
    """
     0  |  4 | uint32 filename size
     4  |  x | char[x] filename
    4+x |  4 | uint32 data size
    x+8 |  y | ?? data (XOR encrypted)
    total size: 4 + x + 4 + y bytes (== section payload size)
    """

    _BLOCK_SIZE = 1024  # we read the file block-wise to save memory

    def __init__(self, fp: BinaryIO, offset: int, size: int):
        self._fp = fp
        self.size = size
        self._file_offset = offset
        self._fp.seek(self._file_offset)
        filename_size = struct.unpack('<I', self._fp.read(4)[:4])[0]
        self.filename = self._fp.read(filename_size).rstrip(b'\x00').decode('ascii', errors='replace')
        self.data_offset = self._file_offset + 4 + filename_size + 4
        self.data_size = struct.unpack('<I', self._fp.read(4))[0]

    def save(self, save_dir: Path):
        output_path = save_dir / self.filename.lstrip('/')
        output_path.parent.mkdir(exist_ok=True, parents=True)
        self._fp.seek(self.data_offset)
        remaining = self.data_size
        with output_path.open('wb') as out_fp:
            while remaining > 0:
                chunk_size = min(self._BLOCK_SIZE, remaining)
                data = self._fp.read(chunk_size)
                if not data:
                    break
                output = _decrypt(data)
                out_fp.write(output)
                remaining -= chunk_size

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


class Pk2Cmd:
    """
    0 | x | char[x] command (XOR encrypted)
    total size: x bytes (== section payload size)
    """

    def __init__(self, fp: BinaryIO, offset: int, size: int):
        fp.seek(offset)
        self.command = _decrypt(fp.read(size)).rstrip(b'\x00').decode('ascii', errors='replace')
        self.size = size

    def __str__(self):
        cmd = repr(self.command)
        return f'CMD: {cmd}'


def _decrypt(data: bytes) -> bytearray:
    output = bytearray()
    for index, char in enumerate(data):
        output.append(char ^ XOR_KEY[index % KEY_LEN])
    return output


def unpack_function(file_path: str, tmp_dir: str):
    input_path, output_dir = Path(file_path), Path(tmp_dir)
    meta = {'sections': []}

    if input_path.stat().st_size < Pk2FileHeader.size + Pk2SectionHeader.size:
        meta['error'] = 'file too small'
        return meta

    with input_path.open('rb') as fp:
        file_header = Pk2FileHeader(fp)
        offset = file_header.size
        meta['header'] = file_header.to_dict()
        for _ in range(file_header.section_count):
            try:
                section_header = Pk2SectionHeader(fp, offset)
                section_meta = section_header.to_dict()
                offset += section_header.size
                if section_header.type == 'FILE':
                    pk2_file = Pk2File(fp, offset, section_header.payload_size)
                    pk2_file.save(output_dir)
                    offset += pk2_file.size
                    section_meta['file'] = pk2_file.to_dict()
                elif section_header.type == 'CMD':
                    pk2_command = Pk2Cmd(fp, offset, section_header.payload_size)
                    offset += pk2_command.size
                    section_meta['command'] = pk2_command.command
                else:
                    meta['error'] = f'unknown section type: {section_header.type}'
                    break
                meta['sections'].append(section_meta)
            except struct.error:
                meta['error'] = f'error while parsing section at offset {offset}'
                break

    return {'output': meta}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
