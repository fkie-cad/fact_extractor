from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestInstarBnegUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/bneg', 'Instar BNEG')

    def test_extraction_bneg(self):
        in_file = TEST_DATA_DIR / 'test.bneg'
        assert in_file.is_file(), 'test file is missing'
        files, meta = self.unpacker.extract_files_from_file(str(in_file), self.tmp_dir.name)
        assert len(files) == 2  # noqa: PLR2004
        assert 'output' in meta
        assert 'size 7' in meta['output']
        assert 'size 8' in meta['output']

        file1 = Path(self.tmp_dir.name) / 'partition_1.bin'
        assert file1.is_file()
        assert file1.read_bytes() == b'foobar\n'
        file2 = Path(self.tmp_dir.name) / 'partition_2.bin'
        assert file2.is_file()
        assert file2.read_bytes() == b'test123\n'
