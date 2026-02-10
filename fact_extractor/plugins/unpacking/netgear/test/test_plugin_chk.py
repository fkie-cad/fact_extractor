from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestNetgearCHK(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/netgear-chk', 'netgear-chk')

    def test_extraction_single_file(self):
        in_file = TEST_DATA_DIR / 'test.chk'
        assert in_file.is_file(), 'test file is missing'
        files, meta_data = self.unpacker.base._extract_files_from_file_using_specific_unpacker(
            str(in_file),
            self.tmp_dir.name,
            self.unpacker.base.unpacker_plugins['firmware/netgear-chk'],
        )
        assert len(files) == 1, 'unpacked file number incorrect'
        file = Path(files[0])
        contents = file.read_bytes()
        assert len(contents) == 18, 'unpacked file size incorrect'
        assert contents.startswith(b'foobar'), 'payload not decrypted correctly'
        assert 'kernel size: 18' in meta_data['output']

    def test_extraction_multi_file(self):
        in_file = TEST_DATA_DIR / 'test2.chk'
        assert in_file.is_file(), 'test file is missing'
        files, meta_data = self.unpacker.base._extract_files_from_file_using_specific_unpacker(
            str(in_file),
            self.tmp_dir.name,
            self.unpacker.base.unpacker_plugins['firmware/netgear-chk'],
        )
        assert len(files) == 2, 'unpacked file number incorrect'
        file = Path(sorted(files)[1])
        contents = file.read_bytes()
        assert len(contents) == 4, 'unpacked file size incorrect'
        assert contents == b'bar\n', 'payload not decrypted correctly'
        assert 'rootfs size: 4' in meta_data['output']
