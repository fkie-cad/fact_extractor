import os
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestDjiUnpacker(TestUnpackerBase):
    def test_unpacker_selection(self):
        self.check_unpacker_selection('firmware/dji-drone', 'DJI_drones')

    def test_extraction(self):
        input_file = os.path.join(TEST_DATA_DIR, 'dji.img')
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(input_file, self.tmp_dir.name)

        assert "'entry_count': 2" in meta_data['output']
        assert len(unpacked_files) >= 2, 'Should contain 2 modules'
        assert (
            f'{self.tmp_dir.name}/m0305_main_controller.module' in unpacked_files
        ), 'At least the m0305_main_controller.module file should be matched'
