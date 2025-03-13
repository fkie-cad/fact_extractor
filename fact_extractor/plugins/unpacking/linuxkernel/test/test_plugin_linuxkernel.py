from pathlib import Path

import pytest

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'

SAMPLE_DATA = b'####-------\x1f\x8b\x08-------\x1f\x8b\x08$$$$BZh$$$$'


class TestLinuxKernelUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('linux/kernel', 'LinuxKernel')

    @pytest.mark.parametrize(
        ('input_file', 'expected'),
        [
            ('bzImage_bzip2', 'vmlinux_BZIP_17001'),
            ('bzImage_gzip', 'vmlinux_GZIP_17001'),
            ('bzImage_lz4', 'vmlinux_LZ4_17001'),
            ('bzImage_lzma', 'vmlinux_LZMA_17001'),
            ('bzImage_lzo', 'vmlinux_LZOP_17001'),
            ('bzImage_xz', 'vmlinux_XZ_17001'),
            ('zImage_be32', 'vmlinux_GZIP_BE32_13068'),
        ],
    )
    def test_extraction_valid_bz_image(self, input_file, expected):
        files, _ = self.unpacker.extract_files_from_file(str(TEST_DATA_DIR / input_file), self.tmp_dir.name)
        assert files == [str(Path(self.tmp_dir.name) / expected)]

    def test_extraction_invalid_image(self):
        files, _ = self.unpacker.extract_files_from_file(str(TEST_DATA_DIR / 'bogus_image.bin'), self.tmp_dir.name)
        assert files == []
