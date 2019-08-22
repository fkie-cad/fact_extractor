import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from binascii import Error

from helperFunctions.file_system import get_test_data_dir
from plugins.unpacking.tektronix.code.tek import unpack_function
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def i_always_crash_binascii(*args, **kwargs):
    raise Error


def i_always_crash_file_not_found(*args, **kwargs):
    raise FileNotFoundError()


class TestTektronixHex(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/tek', 'Tektronix HEX')

    def test_extraction(self):
        files, meta_data = self.unpacker.extract_files_from_file(Path(TEST_DATA_DIR, 'testfile.tek'),
                                                                 self.tmp_dir.name)
        assert files
        content = Path(files[0]).read_bytes()
        assert b'Hello world.' in content
        assert 'Success' in meta_data['output']

    @staticmethod
    def test_extraction_bad_file():
        file_path = Path(get_test_data_dir(), 'test_data_file.bin')

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'Failed to slice tek record' in meta_data['output']

    @staticmethod
    def test_crc_mismatch():
        file_path = Path(TEST_DATA_DIR, 'testfile_crc.tek')

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'CRC mismatch' in meta_data['output']

    @staticmethod
    @patch('binascii.unhexlify', i_always_crash_binascii)
    def test_extraction_decoding_error():
        file_path = Path(TEST_DATA_DIR, 'testfile.tek')

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'Unknown' in meta_data['output']

    @staticmethod
    @patch('pathlib.Path.open', i_always_crash_file_not_found)
    def test_extraction_filenotfound_error():
        file_path = Path(TEST_DATA_DIR, 'testfile2.tek')

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'Failed to open file' in meta_data['output']
