from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestUEFIUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/uefi', 'UEFI')

    def test_extraction(self):
        in_file = TEST_DATA_DIR / 'UEFI.CAP'
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        assert len(files) == 1599, 'file number incorrect'
        assert 'output' in meta_data
