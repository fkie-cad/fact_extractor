import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from plugins.unpacking.ascii85.code.adobe import unpack_function
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def i_always_crash(*args, **kwargs):
    raise ValueError()


def i_always_crash_file_not_found(*args, **kwargs):
    raise FileNotFoundError()


class TestAdobeASCII85(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/adobe85', 'Adobe ASCII85')

    def test_extraction(self):
        files, meta_data = self.unpacker.extract_files_from_file(Path(TEST_DATA_DIR, 'testfile.adobe85'),
                                                                 self.tmp_dir.name)
        assert len(files) == 1
        content = Path(files[0]).read_bytes()
        assert b'test for a FACT plugin' in content
        assert 'Success' in meta_data['output']

    @patch('base64.a85decode', i_always_crash)
    def test_extraction_decoding_error(self):
        file_path = Path(TEST_DATA_DIR, 'testfile.adobe85')

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'Unknown' in meta_data['output']

    @patch('pathlib.Path.open', i_always_crash_file_not_found)
    def test_extraction_filenotfound_error(self):
        file_path = Path(TEST_DATA_DIR, 'testfile2.adobe85')

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'Failed to open file' in meta_data['output']
