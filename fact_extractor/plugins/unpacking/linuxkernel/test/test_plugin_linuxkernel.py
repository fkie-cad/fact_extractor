import os
import sys
from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

CODE_DIR = Path(__file__).parent.parent / 'code'
sys.path.append(str(CODE_DIR))

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

sample_data = b'####-------\x1f\x8b\x08-------\x1f\x8b\x08$$$$BZh$$$$'


class TestPaToolUnpacker(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('linux/kernel', 'LinuxKernel')

    def test_extraction_valid_bzImage(self):
        input_file = TEST_DATA_DIR / 'bzImage'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)

        print('files returned in test: ', files)
        self.assertEqual([os.path.join(self.tmp_dir.name, 'vmlinux_GZIP_17940')], files)

    def test_extraction_invalid_image(self):
        input_file = TEST_DATA_DIR / 'bogus_image.bin'
        files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        self.assertEqual([], files)
