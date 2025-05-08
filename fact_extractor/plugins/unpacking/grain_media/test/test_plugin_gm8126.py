from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestGm8126Unpacker(TestUnpackerBase):
    def test_unpacker_selection(self):
        self.check_unpacker_selection('firmware/gm8126', 'gm8126')

    def test_extraction(self):
        input_file = TEST_DATA_DIR / 'test.gm8126'
        assert input_file.is_file()
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(input_file, self.tmp_dir.name)
        assert len(unpacked_files) == 1
        assert meta_data['output'] == 'Successfully unpacked test.gm8126 to "kernel.img" (size: 10 bytes)'
        file = Path(self.tmp_dir.name) / unpacked_files[0]
        assert file.read_bytes() == b'foobar 123'
