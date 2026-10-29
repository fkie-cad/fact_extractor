"""
This plugin unpacks OpenPGP messages (RFC 4880 / RFC 9580), e.g. firmware images signed with "gpg --sign".
It extracts the contents of the literal data packets. The signatures are not verified (the public key is usually not
available) and encrypted messages cannot be unpacked.
"""

from __future__ import annotations

import bz2
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

NAME = 'OpenPGP'
MIME_PATTERNS = ['application/x-openpgp-message']
VERSION = '0.1.0'

TAG_SIGNATURE = 2
TAG_ONE_PASS_SIGNATURE = 4
TAG_COMPRESSED_DATA = 8
TAG_LITERAL_DATA = 11
ENCRYPTED_TAGS = {
    1: 'public-key encrypted session key',
    3: 'symmetric-key encrypted session key',
    9: 'symmetrically encrypted data',
    18: 'symmetrically encrypted and integrity protected data',
    20: 'AEAD encrypted data',
}
COMPRESSION_ALGORITHMS = {0: 'uncompressed', 1: 'ZIP', 2: 'ZLIB', 3: 'BZip2'}
SUBPACKET_CREATION_TIME = 2
SUBPACKET_ISSUER = 16
SUBPACKET_ISSUER_FINGERPRINT = 33
MAX_NESTING_DEPTH = 8
DEFAULT_FILE_NAME = 'openpgp_literal_data'


class OpenPgpError(Exception):
    pass


class _MessageParser:
    def __init__(self, tmp_dir: str):
        self.tmp_dir = Path(tmp_dir)
        self.log: list[str] = []
        self.signatures: list[dict] = []
        self.encrypted = False

    def parse(self, data: bytes, depth: int = 0) -> int:
        """Parse the packets in `data` and return the offset where parsing stopped (end of the OpenPGP data)."""
        if depth > MAX_NESTING_DEPTH:
            raise OpenPgpError('maximum nesting depth of compressed data packets exceeded')
        offset = 0
        for tag, body, packet_end in _iter_packets(data):
            self._handle_packet(tag, body, depth)
            offset = packet_end
        return offset

    def _handle_packet(self, tag: int, body: bytes, depth: int):
        if tag == TAG_COMPRESSED_DATA:
            algorithm = COMPRESSION_ALGORITHMS.get(body[0], f'unknown ({body[0]})') if body else 'unknown'
            self.log.append(f'compressed data packet ({algorithm})')
            self.parse(_decompress(body), depth + 1)
        elif tag == TAG_LITERAL_DATA:
            self._extract_literal_data(body)
        elif tag == TAG_ONE_PASS_SIGNATURE:
            self.log.append('one-pass signature packet')
        elif tag == TAG_SIGNATURE:
            signature = _parse_signature(body)
            self.signatures.append(signature)
            self.log.append(f'signature packet: {signature}')
        elif tag in ENCRYPTED_TAGS:
            self.encrypted = True
            self.log.append(f'{ENCRYPTED_TAGS[tag]} packet: encrypted messages cannot be unpacked')
        else:
            self.log.append(f'skipping packet with tag {tag}')

    def _extract_literal_data(self, body: bytes):
        if len(body) < 6:  # noqa: PLR2004
            raise OpenPgpError('literal data packet is too short')
        name_length = body[1]
        name = body[2 : 2 + name_length].decode(errors='replace')
        date = _timestamp(body[2 + name_length : 6 + name_length])
        content = body[6 + name_length :]
        output_path = self._get_output_path(name)
        output_path.write_bytes(content)
        self.log.append(f'literal data packet: name "{name}", date {date}, {len(content)} bytes -> {output_path.name}')

    def _get_output_path(self, name: str) -> Path:
        file_name = Path(name).name
        if file_name in ('', '.', '..'):
            file_name = DEFAULT_FILE_NAME
        output_path = self.tmp_dir / file_name
        index = 1
        while output_path.exists():
            output_path = self.tmp_dir / f'{file_name}_{index}'
            index += 1
        return output_path


def _iter_packets(data: bytes) -> Iterator[tuple[int, bytes, int]]:
    """
    Yields the tag, the body and the end offset of each packet.
    Stops at the first byte that is not a valid packet header (e.g. padding or trailing data).
    """
    offset = 0
    while offset < len(data):
        header = data[offset]
        if not header & 0x80:
            return
        if header & 0x40:  # new packet format
            tag = header & 0x3F
            body, offset = _read_new_format_body(data, offset + 1)
        else:
            tag = (header >> 2) & 0x0F
            length_type = header & 0x03
            offset += 1
            if length_type == 3:  # noqa: PLR2004
                # indeterminate length: the packet extends to the end of the data
                body, offset = data[offset:], len(data)
            else:
                length_size = 1 << length_type
                length = _read_int(data, offset, length_size)
                offset += length_size
                body = _read_bytes(data, offset, length)
                offset += length
        yield tag, body, offset


def _read_new_format_body(data: bytes, offset: int) -> tuple[bytes, int]:
    chunks = []
    while True:
        first = _read_int(data, offset, 1)
        partial = False
        if first < 192:  # noqa: PLR2004
            length, offset = first, offset + 1
        elif first < 224:  # noqa: PLR2004
            length, offset = ((first - 192) << 8) + _read_int(data, offset + 1, 1) + 192, offset + 2
        elif first == 255:  # noqa: PLR2004
            length, offset = _read_int(data, offset + 1, 4), offset + 5
        else:  # partial body length: more chunks follow
            length, offset, partial = 1 << (first & 0x1F), offset + 1, True
        chunks.append(_read_bytes(data, offset, length))
        offset += length
        if not partial:
            return b''.join(chunks), offset


def _read_bytes(data: bytes, offset: int, length: int) -> bytes:
    if offset + length > len(data):
        raise OpenPgpError(f'packet at offset {offset} is truncated')
    return data[offset : offset + length]


def _read_int(data: bytes, offset: int, length: int) -> int:
    return int.from_bytes(_read_bytes(data, offset, length), 'big')


def _decompress(body: bytes) -> bytes:
    if not body:
        raise OpenPgpError('compressed data packet is empty')
    algorithm, compressed = body[0], body[1:]
    if algorithm == 0:
        return compressed
    if algorithm in (1, 2):
        decompressor = zlib.decompressobj(-zlib.MAX_WBITS if algorithm == 1 else zlib.MAX_WBITS)
        return decompressor.decompress(compressed) + decompressor.flush()
    if algorithm == 3:  # noqa: PLR2004
        return bz2.BZ2Decompressor().decompress(compressed)
    raise OpenPgpError(f'unknown compression algorithm {algorithm}')


def _parse_signature(body: bytes) -> dict:
    version = body[0] if body else None
    signature: dict[str, int | str | None] = {'version': version}
    if version == 3:  # noqa: PLR2004
        signature['created'] = _timestamp(body[3:7])
        signature['key_id'] = body[7:15].hex().upper()
    elif version in (4, 5, 6):
        length_size = 2 if version == 4 else 4  # noqa: PLR2004
        offset = 4
        for _ in range(2):  # hashed and unhashed subpackets
            length = _read_int(body, offset, length_size)
            offset += length_size
            _parse_subpackets(_read_bytes(body, offset, length), signature)
            offset += length
    return signature


def _parse_subpackets(data: bytes, signature: dict):
    offset = 0
    while offset < len(data):
        first = data[offset]
        if first < 192:  # noqa: PLR2004
            length, offset = first, offset + 1
        elif first < 255:  # noqa: PLR2004
            length, offset = ((first - 192) << 8) + _read_int(data, offset + 1, 1) + 192, offset + 2
        else:
            length, offset = _read_int(data, offset + 1, 4), offset + 5
        subpacket = _read_bytes(data, offset, length)
        offset += length
        if not subpacket:
            continue
        subpacket_type, content = subpacket[0] & 0x7F, subpacket[1:]
        if subpacket_type == SUBPACKET_CREATION_TIME:
            signature['created'] = _timestamp(content)
        elif subpacket_type == SUBPACKET_ISSUER:
            signature['key_id'] = content.hex().upper()
        elif subpacket_type == SUBPACKET_ISSUER_FINGERPRINT:
            signature['fingerprint'] = content[1:].hex().upper()


def _timestamp(raw: bytes) -> str:
    return datetime.fromtimestamp(int.from_bytes(raw, 'big'), tz=timezone.utc).isoformat()


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    Optional: Return a dict with meta information
    """
    parser = _MessageParser(tmp_dir)
    meta = {}
    try:
        meta['size'] = parser.parse(Path(file_path).read_bytes())
    except (OpenPgpError, zlib.error, OSError) as error:
        parser.log.append(f'error: {error}')
    meta['output'] = '\n'.join(parser.log)
    meta['signatures'] = parser.signatures
    meta['encrypted'] = parser.encrypted
    return meta


# ----> Do not edit below this line <----


def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
