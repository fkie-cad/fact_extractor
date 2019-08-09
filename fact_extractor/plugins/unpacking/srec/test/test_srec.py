import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from bincopy import Error

from helperFunctions.file_system import get_test_data_dir
from plugins.unpacking.srec.code.srec import unpack_function
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def i_always_crash_bincopy(*args, **kwargs):
    raise Error()


def i_always_crash_file_not_found(*args, **kwargs):
    raise FileNotFoundError()


class TestMotorolaSrecord(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/srecord', 'Motorola S-Record')

    def test_extraction(self):
        files, meta_data = self.unpacker.extract_files_from_file(Path(TEST_DATA_DIR, 'testfile.srec'),
                                                                 self.tmp_dir.name)
        assert len(files) == 1
        content = Path(files[0]).read_bytes()
        assert b'Hello world.' in content
        assert 'Success' in meta_data['output']

    def test_extraction_bad_file(self):
        file_path = Path(get_test_data_dir(), 'test_data_file.bin')

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'not starting with an \'S\'' in meta_data['output']

    @patch('bincopy.unpack_srec', i_always_crash_bincopy)
    def test_extraction_decoding_error(self):
        file_path = Path(TEST_DATA_DIR, 'testfile.srec')

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'Unknown' in meta_data['output']

    @patch('pathlib.Path.open', i_always_crash_file_not_found)
    def test_extraction_filenotfound_error(self):
        file_path = Path(TEST_DATA_DIR, 'testfile2.srec')

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'Failed to open file' in meta_data['output']
