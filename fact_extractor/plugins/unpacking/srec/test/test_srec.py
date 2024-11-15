from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from helperFunctions.file_system import get_test_data_dir
from plugins.unpacking.srec.code.srec import unpack_function
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


def i_always_crash_file_not_found(*args, **kwargs):
    raise FileNotFoundError()


def successful_extraction(files, meta_data):
    assert files
    content = Path(files[0]).read_bytes()
    assert b'Hello world.' in content
    assert 'Success' in meta_data['output']
    assert files[0].endswith('.bin')


class TestMotorolaSRecord(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/srecord', 'Motorola S-Record')

    def test_extraction(self):
        for srec_file in ['testfile.srec', 'testfile_noS0.srec', 'additional_data.srec']:
            files, meta_data = self.unpacker.extract_files_from_file(TEST_DATA_DIR / srec_file, self.tmp_dir.name)
            successful_extraction(files, meta_data)


def test_extraction_bad_file():
    file_path = Path(get_test_data_dir(), 'test_data_file.bin')

    with TemporaryDirectory() as tmp_dir:
        meta_data = unpack_function(file_path, tmp_dir)

    assert 'Error: no valid srec data found' in meta_data['output']


def test_extraction_decoding_error():
    for srec_file in ['bad_testfile.srec', 'bad_testfile2.srec']:
        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(TEST_DATA_DIR / srec_file, tmp_dir)

        assert 'Unknown' in meta_data['output']


@patch('pathlib.Path.open', i_always_crash_file_not_found)
def test_extraction_filenotfound_error():
    with TemporaryDirectory() as tmp_dir:
        meta_data = unpack_function(TEST_DATA_DIR / 'testfile2.srec', tmp_dir)

    assert 'Failed to open file' in meta_data['output']
