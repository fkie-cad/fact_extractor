from pathlib import Path

from plugins.unpacking.sercomm.code.sercomm import MIME_PATTERNS, NAME
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestSerCommUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        for mime in MIME_PATTERNS:
            self.check_unpacker_selection(mime, NAME)

    def test_extraction_sercomm(self):
        in_file = TEST_DATA_DIR / 'test.bin'
        assert in_file.is_file(), 'test file is missing'
        files, meta = self.unpacker.base.extract_files_from_file(str(in_file), self.tmp_dir.name)
        assert len(files) == 2, 'file number incorrect'
        assert 'output' in meta
        expected_file = 'stream_01_14.bin'
        assert expected_file in meta['output']
        files_by_name = {p.name: p for f in files if (p := Path(f))}
        assert expected_file in files_by_name
        assert files_by_name[expected_file].read_text().startswith('test1234')
