import os
from pathlib import Path

import pytest

from fact_extractor.helperFunctions.file_system import get_test_data_dir
from fact_extractor.test.unit.unpacker.test_unpacker import TestUnpackerBase
from ..code.ros import infer_header_size_from_version, infer_endianness_from_file_count, unpack_function

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestRosUnpacker(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/ros', 'ROSFile')

    def test_extraction(self):
        in_file = os.path.join(TEST_DATA_DIR, 'test.ros')
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        assert len(files) == 6, f'file number incorrect ({files})'
        assert f'{self.tmp_dir.name}/DATETIME_C' in files, 'Not all files found'
        assert 'file_information' in meta_data, 'Output meta not set'


def test_infer_endianness():
    little = b'\x00' * 0x20 + b'\x05\x00\x00\x00'
    big = b'\x00' * 0x20 + b'\x00\x00\x00\x05'
    assert infer_endianness_from_file_count(little) == '<'
    assert infer_endianness_from_file_count(big) == '>'


def test_infer_header_size():
    v1 = b'\x00' * 4 + b'1.01'
    v2 = b'\x00' * 4 + b'2.00'
    unknown = b'\x00' * 4 + b'1.02'

    assert infer_header_size_from_version(v1) == 48
    assert infer_header_size_from_version(v2) == 80

    with pytest.raises(ValueError):
        infer_header_size_from_version(unknown)


def test_unpack_with_bad_file(tmpdir):
    meta_data = unpack_function(str(Path(get_test_data_dir()) / 'generic_carver_test'), str(tmpdir))
    assert 'error' in meta_data
    assert 'Unknown ros header' in meta_data['error']
