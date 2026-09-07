from pathlib import Path

from helperFunctions.magic import from_file
from plugins.unpacking.dlink.code.dlink_deafbead import MIME_PATTERNS, NAME
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'
TEST_FILE = TEST_DATA_DIR / 'test.deafbead'
MIME = MIME_PATTERNS[0]


class TestDLinkDeafbead(TestUnpackerBase):
    def test_unpacker_selection(self):
        self.check_unpacker_selection(MIME, NAME)

    def test_extraction(self):
        files, meta_data = self.unpacker.extract_files_from_file(TEST_FILE, self.tmp_dir.name)
        assert meta_data['plugin_used'] == NAME
        assert meta_data.get('error') is None

        assert len(files) == 3
        assert 'output' in meta_data
        assert 'Successfully unpacked DEAFBEAD container' in meta_data['output']
        files = {p.name: p for f in files if (p := Path(f))}
        assert 'apple.txt' in files
        assert files['apple.txt'].read_bytes() == b'apple\n'

    def test_mime_detection(self):
        assert from_file(TEST_FILE, mime=True) == MIME
