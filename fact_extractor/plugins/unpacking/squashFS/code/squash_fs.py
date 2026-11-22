"""
This plugin unpacks SquashFS filesystem images
"""

import struct
from pathlib import Path
from shlex import split
from subprocess import run

from unblob.handlers.filesystem.squashfs import SquashFSExtractor

NAME = 'SquashFS'
MIME_PATTERNS = ['filesystem/squashfs']
VERSION = '1.0.0'
MAGIC_BE = {
    bytes.fromhex('73 71 73 68'),
    bytes.fromhex('73 71 6c 7a'),
    bytes.fromhex('74 71 73 68'),
    bytes.fromhex('71 73 68 73'),
}
SUPPORTED_VERSIONS = {1, 2, 3, 4}
MAGIC_LE = {bytes(reversed(m)) for m in MAGIC_BE}
VERSION_OFFSET = 28


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    path = Path(file_path)
    with path.open(mode='rb') as fp:
        magic = fp.read(4)
    is_big_endian = _is_big_endian(magic)
    be_magic = int.from_bytes(magic, byteorder='big', signed=False) if is_big_endian else 0
    version = _get_squashfs_version(path, is_big_endian)
    extractor = SquashFSExtractor(version if version in SUPPORTED_VERSIONS else 4, be_magic)
    extractor.extract(path, Path(tmp_dir))
    output = f'SquashFS version: {version}\nEndianness: {"big" if is_big_endian else "little"}\nMagic: {magic.hex(" ")}'
    if superblock_info := _get_superblock_info(path, is_big_endian):
        output += '\n\n' + superblock_info
    return {'output': output}


def _is_big_endian(magic: bytes) -> bool:
    if magic in MAGIC_BE:
        return True
    if magic in MAGIC_LE:
        return False
    raise ValueError(f'is not a SquashFS file (magic: {magic.hex(" ")})')


def _get_squashfs_version(file_path: Path, is_big_endian: bool) -> int:
    with file_path.open(mode='rb') as fp:
        fp.seek(VERSION_OFFSET)
        return struct.unpack('>H' if is_big_endian else '<H', fp.read(2))[0]


def _get_superblock_info(file_path: Path, is_big_endian: bool) -> str:
    proc = run(
        split(f'sasquatch -s {"-be" if is_big_endian else "-le"} {file_path}'),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ''
    return proc.stdout.strip()


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
