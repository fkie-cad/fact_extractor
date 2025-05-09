from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestDlinkMh01(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/dlink-mh01', 'D-Link MH01')

    def test_extraction(self):
        in_file = TEST_DATA_DIR / 'fw_mh01_test.bin'
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        assert len(files) == 3
        name_to_file = {p.name: p for f in files if (p := Path(f))}
        assert 'fw.bin' in name_to_file
        assert name_to_file['fw.bin'].read_text() == 'foobar 1234 test\n'
        assert 'output' in meta_data
        assert 'decryption successful' in meta_data['output']
        assert 'Saved decrypted firmware to fw.bin' in meta_data['output']
