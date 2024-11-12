from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'

EXPECTED_FILE_COUNT = 3


class TestFITUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('linux/device-tree', 'FIT')

    def test_extraction(self):
        test_file_path = Path(TEST_DATA_DIR) / 'fit.itb'
        extracted_files, meta_data = self.unpacker.extract_files_from_file(str(test_file_path), self.tmp_dir.name)

        assert meta_data['plugin_used'] == 'FIT', 'wrong plugin applied'

        assert len(extracted_files) == EXPECTED_FILE_COUNT, 'not all files extracted'
        assert all(
            Path(element).name in ['kernel', 'fdt', 'rootfs'] for element in extracted_files
        ), 'not all files extracted'
