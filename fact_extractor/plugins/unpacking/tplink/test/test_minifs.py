from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'
MIME = 'filesystem/tp-link-minifs'


class TestTpLinkMiniFS(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('filesystem/tp-link-minifs', 'tp-link-minifs')

    def test_extraction(self):
        in_file = TEST_DATA_DIR / 'test.minifs'
        assert in_file.is_file(), 'test file is missing'
        files, meta_data = self.unpacker.base._extract_files_from_file_using_specific_unpacker(
            str(in_file),
            self.tmp_dir.name,
            self.unpacker.base.unpacker_plugins[MIME],
        )
        assert len(files) == 4, 'unpacked file number incorrect'
        file = Path(sorted(files)[0])
        contents = file.read_bytes()
        assert len(contents) == 6, 'unpacked file size incorrect'
        assert contents.startswith(b'apple'), 'payload not decrypted correctly'
        assert 'version: 3' in meta_data['output']
        assert 'file count: 4' in meta_data['output']
