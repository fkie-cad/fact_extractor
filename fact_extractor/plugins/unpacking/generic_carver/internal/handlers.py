from __future__ import annotations

import struct

from unblob.file_utils import File, InvalidInputFormat
from unblob.handlers.compression.zlib import ZlibHandler
from unblob.models import Handler, HexString, ValidChunk


class ZlibCarvingHandler(ZlibHandler):
    NAME = 'zlib_carver'

    PATTERNS = [  # noqa: RUF012
        HexString('78 01'),  # low compression
        HexString('78 9c'),  # default compression
        HexString('78 da'),  # best compression
        HexString('78 5e'),  # compressed
    ]


class Gm8126ImageHandler(Handler):
    NAME = 'gm8126_image'
    HEADER_SIZE = 0x100
    PATTERNS = (HexString('80 5a 47 4d 00 00 00 00'),)

    def calculate_chunk(self, file: File, start_offset: int) -> ValidChunk | None:
        # the file size is at offset 0x8 in the header
        file.seek(start_offset + 8)
        file_size = struct.unpack('>I', file.read(4))[0]
        total_size = self.HEADER_SIZE + file_size
        if total_size > file.size():
            raise InvalidInputFormat('File size is invalid')
        return ValidChunk(
            start_offset=start_offset,
            end_offset=start_offset + total_size,
        )


class PngImageHandler(Handler):
    NAME = 'png'
    PATTERNS = (HexString('89 50 4e 47 0d 0a 1a 0a'),)

    def calculate_chunk(self, file: File, start_offset: int) -> ValidChunk | None:
        size = file.size()
        # there is no size field in the header, but the file consists of chunks with their own headers which have a
        # size field, so we can follow the chunks until we get to the end of the file
        current_offset = start_offset + 8  # the first chunk starts
        while True:
            file.seek(current_offset)
            chunk_size = struct.unpack('>I', file.read(4))[0]
            chunk_type = file.read(4)
            current_offset += 8 + chunk_size + 4  # 4*2 bytes header + chunk size + 4 bytes CRC
            if chunk_type == b'IEND':
                return ValidChunk(
                    start_offset=start_offset,
                    end_offset=current_offset,
                )
            if current_offset > size:
                return None


CUSTOM_HANDLERS = [ZlibCarvingHandler, Gm8126ImageHandler, PngImageHandler]
