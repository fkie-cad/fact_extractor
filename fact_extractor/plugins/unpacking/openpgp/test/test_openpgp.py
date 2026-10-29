from pathlib import Path

import pytest

from helperFunctions.file_system import get_test_data_dir
from plugins.unpacking.openpgp.code.openpgp import (
    MIME_PATTERNS,
    OpenPgpError,
    _read_new_format_body,
    unpack_function,
)
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'
TEST_FILE = Path(get_test_data_dir()) / 'get_files_test' / 'testfile1'
TEST_KEY_ID = 'D6921DFEB6FE4FA9'


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

    def test_extraction_trailing_data(self, tmp_path):
        test_file = tmp_path / 'trailing.gpg'
        content = (TEST_DATA_DIR / 'uncompressed.gpg').read_bytes()
        test_file.write_bytes(content + b'\x00' * 16 + b'trailing data')
        meta = unpack_function(str(test_file), self.tmp_dir.name)
        assert meta['size'] == len(content)
        assert (Path(self.tmp_dir.name) / 'testfile1').is_file()


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
