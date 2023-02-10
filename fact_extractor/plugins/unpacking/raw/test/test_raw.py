# pylint: disable=protected-access
from pathlib import Path
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(Path(__file__).parent, 'data')


class TestRawUnpacker(TestUnpackerBase):

    def test_unpacker_selection(self):
        self.check_unpacker_selection('data/raw', 'RAW')

    def test_extraction(self):
        input_file = Path(TEST_DATA_DIR, 'raw.bin')
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        assert meta_data['padding seperated sections'] == 3
        assert meta_data['LZMA'] == 1
        assert len(unpacked_files) == 4
        assert f'{self.tmp_dir.name}/0x2f' in unpacked_files
        assert f'{self.tmp_dir.name}/0x8d.lzma' in unpacked_files

    def test_extraction_encoded(self):
        input_file = Path(TEST_DATA_DIR, 'encoded.bin')
        unpacked_files, meta_data = self.unpacker._extract_files_from_file_using_specific_unpacker(str(input_file), self.tmp_dir.name, self.unpacker.unpacker_plugins['data/raw'])
        assert meta_data['Intel Hex'] == 1
        assert meta_data['Motorola S-Record'] == 1
        assert f'{self.tmp_dir.name}/0x6.ihex' in unpacked_files
        assert f'{self.tmp_dir.name}/0x291f.srec' in unpacked_files
        assert len(unpacked_files) == 2

    def test_extraction_nothing_included(self):
        input_file = Path(TEST_DATA_DIR, 'nothing.bin')
        unpacked_files, _ = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)
        assert len(unpacked_files) == 0
