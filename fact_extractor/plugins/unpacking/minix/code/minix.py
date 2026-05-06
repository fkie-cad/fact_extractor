"""
This plugin unpacks minix filesystems using unblob.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from unblob.handlers.filesystem.minixfs import MinixFSExtractor

NAME = 'minix'
MIME_PATTERNS = ['filesystem/minix']
VERSION = '0.1.0'

VERSION_TO_EXTRACTOR = {
    1: MinixFSExtractor(version=1),
    2: MinixFSExtractor(version=2),
    3: MinixFSExtractor(version=3),
}
V12_MAGIC_OFFSET = 0x410
V1_MAGIC = {
    # little endian
    bytes.fromhex('7f 13'),
    bytes.fromhex('8f 13'),
    # big endian
    bytes.fromhex('13 7f'),
    bytes.fromhex('13 8f'),
}
V2_MAGIC = {
    # little endian
    bytes.fromhex('68 24'),
    bytes.fromhex('78 24'),
    # big endian
    bytes.fromhex('24 68'),
    bytes.fromhex('24 78'),
}
V3_MAGIC_OFFSET = 0x418
V3_MAGIC = {
    bytes.fromhex('5a 4d'),  # little endian
    bytes.fromhex('4d 5a'),  # big endian
}


def unpack_function(file_path: str, tmp_dir: str) -> dict[str, Any]:
    input_path = Path(file_path)
    version = _get_minix_version(input_path)
    extractor = VERSION_TO_EXTRACTOR[version]
    extractor.extract(input_path, Path(tmp_dir))
    return {'output': f'Successfully unpacked minix v{version} filesystem'}


def _get_minix_version(file_path: Path) -> int:
    with file_path.open('rb') as fp:
        fp.seek(V12_MAGIC_OFFSET)
        magic = fp.read(2)
        if magic in V1_MAGIC:
            return 1
        if magic in V2_MAGIC:
            return 2
        fp.seek(V3_MAGIC_OFFSET)
        magic = fp.read(2)
        if magic in V3_MAGIC:
            return 3
        raise RuntimeError(f'Unexpected magic value {magic}')


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
