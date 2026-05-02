from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestJFFS2Unpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('filesystem/jffs2', 'JFFS2')
        self.check_unpacker_selection('filesystem/jffs2-big', 'JFFS2')

    def test_extraction_big(self):
        meta_data = self.check_unpacking_of_standard_unpack_set(TEST_DATA_DIR / 'jffs2_be.img')
        assert 'Jffs2_raw_inode count: 4' in meta_data['output']

    def test_extraction_little(self):
        meta_data = self.check_unpacking_of_standard_unpack_set(TEST_DATA_DIR / 'jffs2_le.img')
        assert 'Jffs2_raw_inode count: 4' in meta_data['output']

    def test_extraction_trailing_data(self):
        meta_data = self.check_unpacking_of_standard_unpack_set(
            TEST_DATA_DIR / 'jffs2_b2_trailing_data.img', trailing_data=True
        )
        assert 'Jffs2_raw_inode count: 4' in meta_data['output']
        unpacked_files = {f.name: f for f in Path(self.tmp_dir.name).iterdir()}
        assert 'trailing.bin' in unpacked_files
        assert unpacked_files['trailing.bin'].read_bytes().startswith(b'foobar')
