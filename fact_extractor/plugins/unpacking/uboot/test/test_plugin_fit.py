import os

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

class TestFITUnpacker(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('linux/device-tree', 'FIT')

    def test_extraction(self):
        test_file_path = os.path.join(TEST_DATA_DIR, 'fit.itb')
        extracted_files, meta_data = self.unpacker.extract_files_from_file(test_file_path, self.tmp_dir.name)

        assert meta_data['plugin_used'] == 'FIT', 'wrong plugin applied'

        assert len(extracted_files) == 3, 'not all files extracted'
        assert all(element in ['kernel', 'fdt', 'rootfs'] for element in extracted_files), 'not all files extracted'

