import os
import sys
from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

CODE_DIR = Path(__file__).parent.parent / 'code'
sys.path.append(str(CODE_DIR))

TEST_DATA_DIR = Path(__file__).parent / 'data'

sample_data = b'####-------\x1f\x8b\x08-------\x1f\x8b\x08$$$$BZh$$$$'


class TestLinuxKernelUnpacker(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('linux/kernel', 'LinuxKernel')

    def test_extraction_valid_bzImage_bzip2(self):
        input_file = TEST_DATA_DIR / 'bzImage_bzip2'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        self.assertEqual([os.path.join(self.tmp_dir.name, 'vmlinux_BZIP_17001')], files)

    def test_extraction_valid_bzImage_gzip(self):
        input_file = TEST_DATA_DIR / 'bzImage_gzip'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        self.assertEqual([os.path.join(self.tmp_dir.name, 'vmlinux_GZIP_17001')], files)

    def test_extraction_valid_bzImage_lz4(self):
        input_file = TEST_DATA_DIR / 'bzImage_lz4'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        self.assertEqual([os.path.join(self.tmp_dir.name, 'vmlinux_LZ4_17001')], files)

    def test_extraction_valid_bzImage_lzma(self):
        input_file = TEST_DATA_DIR / 'bzImage_lzma'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        self.assertEqual([os.path.join(self.tmp_dir.name, 'vmlinux_LZMA_17001')], files)

    def test_extraction_valid_bzImage_lzo(self):
        input_file = TEST_DATA_DIR / 'bzImage_lzo'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        self.assertEqual([os.path.join(self.tmp_dir.name, 'vmlinux_LZOP_17001')], files)

    def test_extraction_valid_bzImage_xz(self):
        input_file = TEST_DATA_DIR / 'bzImage_xz'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        self.assertEqual([os.path.join(self.tmp_dir.name, 'vmlinux_XZ_17001')], files)

    def test_extraction_invalid_image(self):
        input_file = TEST_DATA_DIR / 'bogus_image.bin'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        self.assertEqual([], files)
