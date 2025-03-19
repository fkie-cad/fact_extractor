from pathlib import Path

import pytest

from helperFunctions.file_system import decompress_test_file
from plugins.unpacking.sevenz.code.sevenz import MIME_PATTERNS
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestSevenZUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        for item in MIME_PATTERNS:
            self.check_unpacker_selection(item, '7z')

    @pytest.mark.parametrize(
        ('test_file', 'prefix'),
        [
            ('test.7z', 'get_files_test'),
            ('test.rar', 'get_files_test'),
            ('cramfs.img', ''),
            ('test.iso', ''),
        ],
    )
    def test_extraction(self, test_file, prefix):
        meta = self.check_unpacking_of_standard_unpack_set(
            TEST_DATA_DIR / test_file,
            additional_prefix_folder=prefix,
            output=True,
        )
        assert 'password' not in meta, 'password incorrectly set'

    @pytest.mark.parametrize(
        ('test_file', 'prefix', 'ignore'),
        [
            ('fat.img.xz', 'get_files_test', None),
            ('hfs.img.xz', 'untitled/get_files_test', None),
            ('ntfs.img.xz', 'get_files_test', {'[SYSTEM]'}),
            ('ext2.img.xz', 'get_files_test', {'Journal'}),
            ('ext3.img.xz', 'get_files_test', {'Journal'}),
            ('ext4.img.xz', 'get_files_test', {'Journal'}),
        ],
    )
    def test_extraction_compressed(self, test_file, prefix, ignore):
        with decompress_test_file(TEST_DATA_DIR / test_file) as file:
            meta = self.check_unpacking_of_standard_unpack_set(
                file, output=True, additional_prefix_folder=prefix, ignore=ignore
            )
            assert 'password' not in meta, 'password incorrectly set'

    @pytest.mark.parametrize('test_file', ['test_password.7z', 'test_password.zip'])
    def test_extraction_password(self, test_file):
        meta = self.check_unpacking_of_standard_unpack_set(
            TEST_DATA_DIR / test_file, additional_prefix_folder='get_files_test', output=True
        )
        assert meta['password'] == 'test', 'password info not set'

    def test_gzip_extraction(self):
        input_file = TEST_DATA_DIR / 'test.gz'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        assert meta_data['plugin_used'] == '7z'
        assert len(files) == 1
        assert Path(files[0]).name == 'test.data'
        assert 'Type = gzip' in meta_data['output']
        assert 'Everything is Ok' in meta_data['output']
