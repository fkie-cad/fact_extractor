from __future__ import annotations

import re
import struct
from enum import IntEnum

from unblob.file_utils import File, InvalidInputFormat
from unblob.handlers.compression.zlib import ZlibHandler
from unblob.models import Handler, HexString, ValidChunk

WHITESPACE = b'\r\n \t'
CHUNK_SIZE = 4096
OVERLAP = 32  # must cover the longest possible end tag match


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


class GifImageHandler(Handler):
    # see https://www.w3.org/Graphics/GIF/spec-gif89a.txt
    NAME = 'gif'
    PATTERNS = (
        HexString('47 49 46 38 37 61'),  # GIF87a
        HexString('47 49 46 38 39 61'),  # GIF89a
    )
    COLOR_TABLE_FLAG = 0b1000_0000
    COLOR_TABLE_SIZE_BITS = 0b0000_0111
    MAGIC_SIZE = 6
    LOGICAL_SCREEN_DESCRIPTOR_SIZE = 7
    IMAGE_DESCRIPTOR_SIZE = 9

    class BlockType(IntEnum):
        EXTENSION_INTRODUCER = 0x21
        IMAGE_DESCRIPTOR = 0x2C
        TRAILER = 0x3B

    @staticmethod
    def _skip_sub_blocks(file: File, offset: int, size: int) -> int:
        # sub-block structure: <length byte><data bytes...>
        # terminated by a "block terminator": a block with 0x00 length byte and no data
        while offset < size:
            file.seek(offset)
            block_size = ord(file.read(1))
            offset += 1
            if block_size == 0:  # block terminator
                return offset
            offset += block_size  # skip current sub-block
        raise ValueError

    def calculate_chunk(self, file: File, start_offset: int) -> ValidChunk | None:
        try:
            end_offset = self._find_end_offset(file, start_offset)
            return ValidChunk(start_offset=start_offset, end_offset=end_offset)
        except (ValueError, TypeError):
            pass
        return None

    def _find_end_offset(self, file: File, start_offset: int) -> int:
        size = file.size()

        # Logical Screen Descriptor follows directly after the 6 byte magic
        current_offset = start_offset + self.MAGIC_SIZE
        file.seek(current_offset)
        lsd = file.read(self.LOGICAL_SCREEN_DESCRIPTOR_SIZE)
        if len(lsd) < self.LOGICAL_SCREEN_DESCRIPTOR_SIZE:
            raise ValueError
        packed_fields = lsd[4]
        current_offset += self.LOGICAL_SCREEN_DESCRIPTOR_SIZE

        current_offset += self._skip_color_table(packed_fields)  # Global Color Table

        while current_offset < size:
            file.seek(current_offset)
            block_type = ord(file.read(1))
            current_offset += 1

            match block_type:
                case self.BlockType.TRAILER:  # trailer -> found end of file
                    return current_offset

                case self.BlockType.EXTENSION_INTRODUCER:
                    current_offset += 1
                    current_offset = self._skip_sub_blocks(file, current_offset, size)

                case self.BlockType.IMAGE_DESCRIPTOR:
                    file.seek(current_offset)
                    img_desc = file.read(self.IMAGE_DESCRIPTOR_SIZE)
                    if len(img_desc) < self.IMAGE_DESCRIPTOR_SIZE:
                        raise ValueError
                    packed_fields = img_desc[8]
                    current_offset += self.IMAGE_DESCRIPTOR_SIZE

                    current_offset += self._skip_color_table(packed_fields)  # local color table

                    current_offset += 1  # LZW Minimum Code Size
                    current_offset = self._skip_sub_blocks(file, current_offset, size)

                case _:  # unknown block Type -> abort
                    raise ValueError

        raise ValueError  # reached end without finding trailer

    def _skip_color_table(self, packed_fields: int) -> int:
        if packed_fields & self.COLOR_TABLE_FLAG:  # color tables are optional
            entry_count = 2 ** ((packed_fields & self.COLOR_TABLE_SIZE_BITS) + 1)
            return entry_count * 3
        return 0


class JpegImageHandler(Handler):
    # see https://www.w3.org/Graphics/JPEG/itu-t81.pdf (ITU-T T.81)
    NAME = 'jpeg'
    PATTERNS = (
        HexString('FF D8 FF'),  # SOI followed by the first marker's FF
    )
    MARKER_PREFIX = 0xFF
    STUFFED_BYTE = 0x00  # FF 00 -> literal 0xFF inside entropy-coded data

    class Marker(IntEnum):
        SOI = 0xD8  # Start Of Image
        EOI = 0xD9  # End Of Image
        SOS = 0xDA  # Start Of Scan (entropy-coded data follows, no length)
        TEM = 0x01  # standalone, no length field
        RST0 = 0xD0  # restart markers RST0..RST7: standalone, no length field
        RST7 = 0xD7
        # Start Of Frame markers: SOF0..SOF15 (0xC0..0xCF),
        # excluding DHT (0xC4), JPG (0xC8) and DAC (0xCC)
        SOF0 = 0xC0
        SOF15 = 0xCF

    @staticmethod
    def _is_start_of_frame(marker: int) -> bool:
        # SOF0..SOF15 except DHT (0xC4), JPG (0xC8), DAC (0xCC)
        return JpegImageHandler.Marker.SOF0 <= marker <= JpegImageHandler.Marker.SOF15 and marker not in (
            0xC4,
            0xC8,
            0xCC,
        )

    @staticmethod
    def _read_marker(file: File, offset: int, size: int) -> tuple[int, int]:
        file.seek(offset)
        if ord(file.read(1)) != JpegImageHandler.MARKER_PREFIX:
            raise ValueError  # expected a marker here
        offset += 1
        while offset < size:
            file.seek(offset)
            marker = ord(file.read(1))
            offset += 1
            if marker != JpegImageHandler.MARKER_PREFIX:  # skip fill bytes
                return marker, offset
        raise ValueError

    def _skip_scan_data(self, file: File, offset: int, size: int) -> int:
        while offset < size:
            file.seek(offset)
            if ord(file.read(1)) != self.MARKER_PREFIX:
                offset += 1
                continue
            file.seek(offset + 1)
            following = ord(file.read(1))
            if following == self.STUFFED_BYTE or (self.Marker.RST0 <= following <= self.Marker.RST7):
                offset += 2  # part of the scan data
                continue
            return offset  # real marker -> scan finished
        raise ValueError

    def calculate_chunk(self, file: File, start_offset: int) -> ValidChunk | None:
        try:
            end_offset = self._find_end_offset(file, start_offset)
            return ValidChunk(start_offset=start_offset, end_offset=end_offset)
        except (ValueError, TypeError):
            pass
        return None

    def _find_end_offset(self, file: File, start_offset: int) -> int:  # noqa: C901
        size = file.size()

        # skip the SOI marker (FF D8)
        marker, current_offset = self._read_marker(file, start_offset, size)
        if marker != self.Marker.SOI:
            raise ValueError

        seen_frame = False
        seen_scan = False

        while current_offset < size:
            marker, current_offset = self._read_marker(file, current_offset, size)

            match marker:
                case self.Marker.EOI:
                    # a valid image must contain a frame header and at least one scan
                    if not (seen_frame and seen_scan):
                        raise ValueError
                    return current_offset

                case self.Marker.TEM:  # standalone markers -> no length, no payload
                    continue
                case _ if self.Marker.RST0 <= marker <= self.Marker.RST7:
                    continue

                case _:  # segment with a 2-byte big-endian length field
                    file.seek(current_offset)
                    length_bytes = file.read(2)
                    if len(length_bytes) < 2:  # noqa: PLR2004
                        raise ValueError
                    segment_length = int.from_bytes(length_bytes, 'big')
                    if segment_length < 2:  # length includes its own 2 bytes  # noqa: PLR2004
                        raise ValueError  # invalid -> avoid rewind/loop
                    current_offset += segment_length

                    if self._is_start_of_frame(marker):
                        seen_frame = True

                    if marker == self.Marker.SOS:
                        seen_scan = True
                        current_offset = self._skip_scan_data(file, current_offset, size)

        raise ValueError  # reached end without a valid EOI


class HtmlHandler(Handler):
    NAME = 'html'
    PATTERNS = (
        HexString('3c ( 68 | 48 ) ( 74 | 54 ) ( 6d | 4d ) ( 6c | 4c ) ( 3e | 20 )'),  # <html> / <HTML
        HexString(
            '3c 21 ( 44 | 64 ) ( 4f | 6f ) ( 43 | 63 ) ( 54 | 74 ) ( 59 | 79 ) ( 50 | 70 ) ( 45 | 65 ) 20'
        ),  # <!DOCTYPE
    )
    END_TAG_PATTERN = re.compile(rb'</\s*html\s*>', re.IGNORECASE)

    def calculate_chunk(self, file: File, start_offset: int) -> ValidChunk | None:
        size = file.size()
        current_offset = start_offset

        while current_offset < size:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break

            if (match := self.END_TAG_PATTERN.search(chunk)) is not None:
                end_offset = _skip_trailing_whitespace(file, current_offset + match.end(), size)
                return ValidChunk(start_offset=start_offset, end_offset=end_offset)

            if len(chunk) < CHUNK_SIZE:  # EOF reached without an end tag
                break
            current_offset += len(chunk) - OVERLAP
            file.seek(current_offset)

        return None


class XmlHandler(Handler):
    NAME = 'xml'
    PATTERNS = (
        HexString('3c 3f ( 78 | 58 ) ( 6d | 4d ) ( 6c | 4c )'),  # <?xml / <?XML
        HexString('3c ( 78 | 58 ) ( 6d | 4d ) ( 6c | 4c ) ( 3e | 20 )'),  # <xml> / <XML
    )
    ROOT_TAG_PATTERN = re.compile(rb'<\s*([A-Za-z_][\w.:-]*)')
    MAX_PROLOG_SIZE = 64 * 1024
    MAX_DOCUMENT_SIZE = 16 * 1024 * 1024

    def calculate_chunk(self, file: File, start_offset: int) -> ValidChunk | None:
        size = file.size()
        data = file.read(min(self.MAX_DOCUMENT_SIZE, size - start_offset))

        root_name, root_start = self._find_root_element(data)
        end_offset = start_offset + self._find_closing_tag(data, root_name, root_start)
        end_offset = _skip_trailing_whitespace(file, end_offset, size)
        return ValidChunk(start_offset=start_offset, end_offset=end_offset)

    @classmethod
    def _find_root_element(cls, data: bytes) -> tuple[bytes, int]:
        offset = data.find(b'>') + 1  # end of <?xml ... ?> or <xml>
        if offset == 0:
            raise InvalidInputFormat('Unterminated XML declaration.')

        limit = min(len(data), cls.MAX_PROLOG_SIZE)
        while offset < limit:
            if data[offset] in WHITESPACE:
                offset += 1
            elif data.startswith(b'<!--', offset):
                closing = data.find(b'-->', offset)
                if closing == -1:
                    raise InvalidInputFormat('Unterminated XML comment.')
                offset = closing + 3
            elif data.startswith(b'<?', offset) or data.startswith(b'<!', offset):
                closing = data.find(b'>', offset)  # processing instruction or doctype
                if closing == -1:
                    raise InvalidInputFormat('Unterminated XML prolog element.')
                offset = closing + 1
            elif (match := cls.ROOT_TAG_PATTERN.match(data, offset)) is not None:
                return match.group(1), offset
            else:
                raise InvalidInputFormat('Invalid XML root element.')
        raise InvalidInputFormat('No XML root element found.')

    @staticmethod
    def _find_closing_tag(data: bytes, root_name: bytes, root_start: int) -> int:
        tag_pattern = re.compile(rb'<\s*(/?)' + re.escape(root_name) + rb'(?![\w.:-])([^>]*)>')
        depth = 0
        for match in tag_pattern.finditer(data, root_start):
            is_closing, attributes = match.group(1), match.group(2)
            if is_closing:
                depth -= 1
                if depth == 0:
                    return match.end()
            elif attributes.rstrip().endswith(b'/'):
                if depth == 0:  # self-closing root element
                    return match.end()
            else:
                depth += 1
        raise InvalidInputFormat('Unbalanced or truncated XML document.')


def _skip_trailing_whitespace(file: File, offset: int, size: int) -> int:
    while offset < size:
        file.seek(offset)
        if file.read(1)[0] not in WHITESPACE:
            break
        offset += 1
    return offset


CUSTOM_HANDLERS = [
    GifImageHandler,
    Gm8126ImageHandler,
    HtmlHandler,
    JpegImageHandler,
    PngImageHandler,
    XmlHandler,
    ZlibCarvingHandler,
]
