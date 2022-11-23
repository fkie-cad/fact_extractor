from pathlib import Path
from tempfile import TemporaryDirectory

from helperFunctions.file_system import decompress_test_file
from test.unit.unpacker.test_unpacker import TestUnpackerBase
from ..code.generic_fs import _extract_loop_devices, _mount_single_filesystem, TYPES

TEST_DATA_DIR = Path(__file__).parent / 'data'
KPARTX_OUTPUT = '''
add map loop7p1 (253:0): 0 7953 linear 7:7 2048
add map loop7p2 (253:1): 0 10207 linear 7:7 10240
'''


class TestGenericFsUnpacker(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('filesystem/btrfs', 'genericFS')
        self.check_unpacker_selection('filesystem/dosmbr', 'genericFS')
        self.check_unpacker_selection('filesystem/f2fs', 'genericFS')
        self.check_unpacker_selection('filesystem/jfs', 'genericFS')
        self.check_unpacker_selection('filesystem/minix', 'genericFS')
        self.check_unpacker_selection('filesystem/reiserfs', 'genericFS')
        self.check_unpacker_selection('filesystem/romfs', 'genericFS')
        self.check_unpacker_selection('filesystem/udf', 'genericFS')
        self.check_unpacker_selection('filesystem/xfs', 'genericFS')

    def test_extraction_romfs(self):
        self.check_unpacking_of_standard_unpack_set(TEST_DATA_DIR / 'romfs.img')

    def test_extraction_btrfs(self):
        with decompress_test_file(TEST_DATA_DIR / 'btrfs.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(test_file, additional_prefix_folder='get_files_test')

    def test_extraction_jfs(self):
        with decompress_test_file(TEST_DATA_DIR / 'jfs.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(test_file, additional_prefix_folder='get_files_test')

    def test_extraction_minix(self):
        with decompress_test_file(TEST_DATA_DIR / 'minix.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(test_file, additional_prefix_folder='get_files_test')

    def test_extraction_reiserfs(self):
        with decompress_test_file(TEST_DATA_DIR / 'reiserfs.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(test_file, additional_prefix_folder='get_files_test')

    def test_extraction_udf(self):
        with decompress_test_file(TEST_DATA_DIR / 'udf.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(test_file, additional_prefix_folder='get_files_test')

    def test_extraction_xfs(self):
        with decompress_test_file(TEST_DATA_DIR / 'xfs.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(test_file, additional_prefix_folder='get_files_test')

    def test_extraction_f2fs(self):
        with decompress_test_file(TEST_DATA_DIR / 'f2fs.img.xz') as test_file:
            self.check_unpacking_of_standard_unpack_set(test_file, additional_prefix_folder='get_files_test')

    def test_extract_multiple_partitions(self):
        with decompress_test_file(TEST_DATA_DIR / 'mbr.img.xz') as test_file:
            files, meta_data = self.unpacker.extract_files_from_file(str(test_file), self.tmp_dir.name)
            expected = [
                str(Path(self.tmp_dir.name, *file_path)) for file_path in [
                    ('partition_0', 'test_data_file.bin'),
                    ('partition_1', 'yara_test_file'),
                    ('partition_2', 'testfile1')
                ]
            ]

            assert 'output' in meta_data
            assert len(files) == 3, 'file number incorrect'
            assert sorted(files) == sorted(expected), 'wrong files extracted'


def test_extract_loop_devices():
    loop_devices = _extract_loop_devices(KPARTX_OUTPUT)
    assert loop_devices
    assert loop_devices == ['loop7p1', 'loop7p2']


def test_unknown_filesystem():
    try:
        TYPES['foobar'] = 'foobar'
        with TemporaryDirectory() as tmp_dir:
            output = _mount_single_filesystem(TEST_DATA_DIR / 'romfs.img', 'foobar', tmp_dir)
        assert 'you may need to install additional kernel modules' in output
    finally:
        TYPES.pop('foobar')
