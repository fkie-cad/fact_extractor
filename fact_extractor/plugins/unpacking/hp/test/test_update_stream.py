from pathlib import Path
from test.unit.unpacker.test_unpacker import TestUnpackerBase

from common_helper_files.fail_safe_file_operations import get_binary_from_file

TEST_DATA_DIR = Path(Path(__file__).parent, 'data')


class TestHpStreamUnpacker(TestUnpackerBase):

    def test_unpacker_selection(self):
        self.check_unpacker_selection('firmware/hp-us', 'HP-Stream')

    def test_extraction(self):
        input_file = Path(TEST_DATA_DIR, 'update_stream.bin')
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        assert meta_data['number_of_zero_padded_sections'] == 4
        assert meta_data['number_of_lzma_streams'] == 1
        assert len(unpacked_files) == 5
        assert f'{self.tmp_dir.name}/0x0' in unpacked_files
        assert f'{self.tmp_dir.name}/0x8d_lzma_decompressed' in unpacked_files
        decompressed_data = get_binary_from_file(f'{self.tmp_dir.name}/0x8d_lzma_decompressed')
        assert decompressed_data == b'compressed_stream_data'
