from pathlib import Path
from fact_extractor.test.unit.unpacker.test_unpacker import TestUnpackerBase


TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestDlinkShrs(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/dlink-shrs', 'D-Link SHRS')

    def test_extraction(self):
        in_file = TEST_DATA_DIR / 'test.dec'
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        assert len(files) == 1
        assert 'output' in meta_data
        file_content = Path(files[0]).read_text()
        assert 'This is a decrypted test file!' in file_content
