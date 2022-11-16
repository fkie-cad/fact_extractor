from pathlib import Path

from helperFunctions.file_system import decompress_test_file
from plugins.unpacking.sevenz.code.sevenz import MIME_PATTERNS
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestSevenZUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        for item in MIME_PATTERNS:
            self.check_unpacker_selection(item, '7z')

    def test_extraction_7z(self):
        self.check_unpacking_of_standard_unpack_set(
            TEST_DATA_DIR / 'test.7z',
            additional_prefix_folder='get_files_test',
            output=True,
        )

    def test_extraction_cramfs(self):
        self.check_unpacking_of_standard_unpack_set(
            TEST_DATA_DIR / 'cramfs.img',
            output=True,
        )

    def test_extraction_fat(self):
        with decompress_test_file(TEST_DATA_DIR / 'fat.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(
                test_file, output=True, additional_prefix_folder='get_files_test'
            )

    def test_extraction_hfs(self):
        with decompress_test_file(TEST_DATA_DIR / 'hfs.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(
                test_file, output=True, additional_prefix_folder='untitled/get_files_test'
            )

    def test_extraction_ntfs(self):
        with decompress_test_file(TEST_DATA_DIR / 'ntfs.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(
                test_file, output=True, additional_prefix_folder='get_files_test', ignore={'[SYSTEM]'}
            )

    def test_extraction_ext(self):
        for index in [2, 3, 4]:
            with decompress_test_file(TEST_DATA_DIR / f'ext{index}.img.xz') as test_file:
                self.check_unpacking_of_standard_unpack_set(
                    test_file, output=True, additional_prefix_folder='get_files_test', ignore={'Journal'}
                )

    def test_extraction_password(self):
        meta = self.check_unpacking_of_standard_unpack_set(
            TEST_DATA_DIR / 'test_password.7z', additional_prefix_folder="get_files_test", output=True
        )
        assert meta['password'] == 'test', 'password info not set'
