from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestRomFsUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('filesystem/romfs', 'romfs')

    def test_extraction(self):
        meta = self.check_unpacking_of_standard_unpack_set(TEST_DATA_DIR / 'romfs.img')
        assert meta['plugin_used'] == 'romfs'
