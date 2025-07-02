from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'

EXPECTED_FILE_COUNT = 4


class TestMaxLinearUImageV2Unpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/maxlinear-uimage-v2', 'MaxLinear UImage')

    def test_extraction(self):
        test_file_path = Path(TEST_DATA_DIR) / 'maxlinear-uimage-v2.bin'
        extracted_files, meta_data = self.unpacker.extract_files_from_file(str(test_file_path), self.tmp_dir.name)

        assert meta_data['plugin_used'] == 'MaxLinear UImage', 'wrong plugin applied'

        assert len(extracted_files) >= EXPECTED_FILE_COUNT, 'not all files extracted'
        file_names = {Path(f).name for f in extracted_files}
        expected_files = ['atomkernel.img', 'atomrootfs.hsqs', 'armkernel.img', 'armrootfs.hsqs']
        assert all(f in file_names for f in expected_files), 'not all files extracted'
