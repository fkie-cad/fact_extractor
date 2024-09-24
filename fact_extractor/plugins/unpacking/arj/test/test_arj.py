from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_FILE = Path(__file__).parent / 'data' / 'test.arj'


class TestArjUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('application/x-arj', 'ARJ')

    def test_extraction(self):
        files, meta_data = self.unpacker.extract_files_from_file(str(TEST_FILE), self.tmp_dir.name)

        assert len(set(files)) == 2, 'file number incorrect'

        assert all(any(Path(extracted).name == file for extracted in files) for file in ['testfile1', 'testfile2'])

        assert 'output' in meta_data
