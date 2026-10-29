import bz2
import random
import zlib
from pathlib import Path

import pytest

from helperFunctions.file_system import get_test_data_dir
from plugins.unpacking.openpgp.code.openpgp import (
    MIME_PATTERNS,
    TAG_LITERAL_DATA,
    OpenPgpError,
    _read_new_format_body,
    unpack_function,
)
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'
TEST_FILE = Path(get_test_data_dir()) / 'get_files_test' / 'testfile1'
TEST_KEY_ID = 'D6921DFEB6FE4FA9'


def _deflate(data: bytes) -> bytes:
    compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
    return compressor.compress(data) + compressor.flush()


class TestOpenPgpUnpacker(TestUnpackerBase):
    def test_unpacker_selection(self):
        for mime in MIME_PATTERNS:
            self.check_unpacker_selection(mime, 'OpenPGP')

    @pytest.mark.parametrize(
        ('file_name', 'compression'),
        [
            ('zip.gpg', 'ZIP'),
            ('zlib.gpg', 'ZLIB'),
            ('bzip2.gpg', 'BZip2'),
            ('uncompressed.gpg', None),
            ('stdin.gpg', None),  # new packet format
        ],
    )
    def test_extraction(self, file_name, compression):
        meta = unpack_function(str(TEST_DATA_DIR / file_name), self.tmp_dir.name)
        extracted = list(Path(self.tmp_dir.name).iterdir())
        assert len(extracted) == 1
        assert extracted[0].name == 'testfile1'
        assert extracted[0].read_bytes() == TEST_FILE.read_bytes()
        assert meta['encrypted'] is False
        assert meta['size'] == (TEST_DATA_DIR / file_name).stat().st_size
        assert len(meta['signatures']) == 1
        assert meta['signatures'][0]['key_id'] == TEST_KEY_ID
        assert meta['signatures'][0]['fingerprint'].endswith(TEST_KEY_ID)
        assert 'created' in meta['signatures'][0]
        if compression:
            assert f'compressed data packet ({compression})' in meta['output']

    def test_extraction_encrypted(self):
        meta = unpack_function(str(TEST_DATA_DIR / 'encrypted.gpg'), self.tmp_dir.name)
        assert not list(Path(self.tmp_dir.name).iterdir())
        assert meta['encrypted'] is True
        assert 'encrypted messages cannot be unpacked' in meta['output']

    def test_extraction_truncated(self, tmp_path):
        truncated = tmp_path / 'truncated.gpg'
        truncated.write_bytes((TEST_DATA_DIR / 'uncompressed.gpg').read_bytes()[:40])
        meta = unpack_function(str(truncated), self.tmp_dir.name)
        assert not list(Path(self.tmp_dir.name).iterdir())
        assert 'truncated' in meta['output']

    @pytest.mark.parametrize('file_name', ['zip.gpg', 'zlib.gpg', 'bzip2.gpg', 'uncompressed.gpg', 'stdin.gpg'])
    @pytest.mark.parametrize(
        'trailing_data', [b'\x00' * 16 + b'trailing data', b'\xff' * 2048], ids=['null-padded', 'ff-padding']
    )
    def test_extraction_trailing_data(self, tmp_path, file_name, trailing_data):
        test_file = tmp_path / 'trailing.gpg'
        content = (TEST_DATA_DIR / file_name).read_bytes()
        test_file.write_bytes(content + trailing_data)
        meta = unpack_function(str(test_file), self.tmp_dir.name)
        assert meta['size'] == len(content)
        assert (Path(self.tmp_dir.name) / 'testfile1').read_bytes() == TEST_FILE.read_bytes()

    def test_extraction_null_byte_in_file_name(self, tmp_path):
        body = b'b\x03a\x00b' + b'\x00' * 4 + b'content'
        test_file = tmp_path / 'null_byte.gpg'
        test_file.write_bytes(bytes([0xC0 | TAG_LITERAL_DATA, len(body)]) + body)
        meta = unpack_function(str(test_file), self.tmp_dir.name)
        assert meta['size'] == len(body) + 2
        assert (Path(self.tmp_dir.name) / 'a_b').read_bytes() == b'content'

    def test_extraction_file_name_exceeds_packet(self, tmp_path):
        body = b'b\xff' + b'\x00' * 4 + b'content'
        test_file = tmp_path / 'long_name.gpg'
        test_file.write_bytes(bytes([0xC0 | TAG_LITERAL_DATA, len(body)]) + body)
        meta = unpack_function(str(test_file), self.tmp_dir.name)
        assert not list(Path(self.tmp_dir.name).iterdir())
        assert 'literal data packet is too short' in meta['output']

    @pytest.mark.parametrize(
        ('algorithm', 'compress'),
        [
            (1, _deflate),
            (2, zlib.compress),
            (3, bz2.compress),
        ],
    )
    def test_extraction_truncated_compressed_data(self, tmp_path, algorithm, compress):
        # old format literal data packet with indeterminate length (i.e. it is not truncated by itself)
        literal_packet = bytes([0x80 | TAG_LITERAL_DATA << 2 | 3]) + b'b\x04test' + b'\x00' * 4
        compressed = compress(literal_packet + random.Random(0).randbytes(4096))
        test_file = tmp_path / 'truncated_compressed.gpg'
        test_file.write_bytes(bytes([0xA3, algorithm]) + compressed[: len(compressed) // 2])
        meta = unpack_function(str(test_file), self.tmp_dir.name)
        assert not list(Path(self.tmp_dir.name).iterdir())
        assert 'compressed data is truncated' in meta['output']


@pytest.mark.parametrize(
    ('data', 'expected_body', 'expected_offset'),
    [
        (b'\x03abc', b'abc', 4),
        (b'\xc0\x01' + b'a' * 193, b'a' * 193, 195),
        (b'\xff\x00\x00\x00\x02ab', b'ab', 7),
        # partial body lengths: 2 bytes, then 4 bytes, then the final 3 bytes
        (b'\xe1ab\xe2cdef\x03ghi', b'abcdefghi', 12),
    ],
)
def test_read_new_format_body(data, expected_body, expected_offset):
    assert _read_new_format_body(data, 0) == (expected_body, expected_offset)


def test_read_new_format_body_truncated():
    with pytest.raises(OpenPgpError):
        _read_new_format_body(b'\x05abc', 0)
