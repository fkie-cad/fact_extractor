from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestBuffaloUnpacker(TestUnpackerBase):
    def test_unpacker_selection(self):
        self.check_unpacker_selection('firmware/buffalo', 'buffalo_bgn')

    def test_extraction(self):
        input_file = TEST_DATA_DIR / 'buffalo.bin'
        assert input_file.is_file()
        unpacked_files, meta = self.unpacker.extract_files_from_file(input_file, self.tmp_dir.name)
        assert len(unpacked_files) == 1
        assert 'output' in meta
        assert 'test-product' in meta['output']
        content = (Path(self.tmp_dir.name) / unpacked_files[0]).read_bytes()
        assert content == b'foobar 123 test\n'
