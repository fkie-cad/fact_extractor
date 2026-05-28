"""
This plugin unpacks firmware images of old SerComm routers.
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

NAME = 'SerComm firmware'
MIME_PATTERNS = ['firmware/sercomm']
VERSION = '0.1.0'
PAYLOAD_OFFSET = 0x200
STREAM_MIN_SIZE = 256
RAW_FORMAT = -15  # raw DEFLATE stream
MARKER = b'\x03\x00\x00\x00'  # DEFLATE streams start after this marker


@dataclass
class DecompressedStream:
    offset: int
    data: bytes
    compressed_size: int
    uncompressed_size: int


def find_streams(data: bytes) -> Iterator[DecompressedStream]:
    """searches for and decompresses DEFLATE streams"""
    offset = 0
    payload_size = len(data)
    while True:
        offset = data.find(MARKER, offset)
        if offset == -1:
            break
        stream_offset = offset + 4
        if stream_offset >= payload_size:
            break
        compressed_size = None
        try:
            decompressor = zlib.decompressobj(RAW_FORMAT)
            result = decompressor.decompress(data[stream_offset:])
            if len(result) >= STREAM_MIN_SIZE:
                compressed_size = payload_size - stream_offset - len(decompressor.unused_data)
                yield DecompressedStream(
                    offset=PAYLOAD_OFFSET + stream_offset,
                    data=result,
                    compressed_size=compressed_size,
                    uncompressed_size=len(result),
                )
        except zlib.error:
            pass
        offset += compressed_size or 1


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    path = Path(file_path)
    output_dir = Path(tmp_dir)
    output = []

    with path.open('rb') as fp:
        fp.seek(PAYLOAD_OFFSET)
        content = fp.read()

    for index, stream in enumerate(find_streams(content), 1):
        output_path = output_dir / f'stream_{index:02d}_{stream.offset}.bin'
        output_path.write_bytes(stream.data)
        ratio = stream.uncompressed_size / stream.compressed_size
        output.append(
            f'decompressed DEFLATE stream {index} '
            f'(offset 0x{stream.offset:x} — 0x{stream.offset + stream.compressed_size:x}) to {output_path.name} '
            f'(compressed size: {stream.compressed_size} bytes, uncompressed size: {stream.uncompressed_size} bytes, '
            f'ratio: {ratio:.2f})'
        )

    return {'output': '\n'.join(output)}


# ----> Do not edit below this line <----


def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
