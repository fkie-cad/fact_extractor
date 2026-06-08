from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestDlinkDWL(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/dlink-dwl', 'D-Link DWL')

    def test_extraction(self):
        in_file = TEST_DATA_DIR / 'test.dwl'
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        assert len(files) == 1
        name_to_file = {p.name: p for f in files if (p := Path(f))}
        assert 'dwl-1337ap.decrypted' in name_to_file
        assert name_to_file['dwl-1337ap.decrypted'].read_text() == 'foobar\\ntest 1234\n'
        assert 'output' in meta_data
        assert 'Successfully decrypted file with aes-256-cbc' in meta_data['output']
