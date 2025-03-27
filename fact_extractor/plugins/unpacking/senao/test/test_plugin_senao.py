from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestGenericCarver(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('generic/carver', 'generic_carver')

    def test_extraction(self):
        in_file = TEST_DATA_DIR / 'testfw_1.enc'
        assert in_file.is_file(), 'test file is missing'
        files, meta_data = self.unpacker._extract_files_from_file_using_specific_unpacker(
            str(in_file),
            self.tmp_dir.name,
            self.unpacker.unpacker_plugins['firmware/senao-v2b'],
        )
        assert len(files) == 1, 'unpacked file number incorrect'
        file = Path(files[0])
        contents = file.read_bytes()
        assert len(contents) == 44, 'unpacked file size incorrect'
        assert contents.startswith(b'foobar'), 'payload not decrypted correctly'
        assert meta_data['output'].startswith('Found payload')
