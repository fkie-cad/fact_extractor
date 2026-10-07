from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestDlinkDcs(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/dlink-dcs', 'd-link dcs')
        self.check_unpacker_selection('firmware/dlink-dcs-enc', 'd-link dcs')

    def test_extraction(self):
        in_file = TEST_DATA_DIR / 'test_dcs.bin'
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        assert len(files) == 2
        name_to_file = {p.name: p for f in files if (p := Path(f))}
        assert 'section_000' in name_to_file
        assert name_to_file['section_000'].read_text() == 'foobar\\ntest 1234\n'
        assert 'output' in meta_data
        assert 'saved as section_000' in meta_data['output']
