from pathlib import Path

from plugins.unpacking.xiaomi_hdr.code.xiaomi_hdr import MIME_PATTERNS
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestXiaomiHdrUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        for mime in MIME_PATTERNS:
            self.check_unpacker_selection(mime, 'Xiaomi HDR')

    def test_extraction_hdr(self):
        in_file = TEST_DATA_DIR / 'test.hdr1'
        assert in_file.is_file(), 'test file is missing'
        meta = self.check_unpacking_of_standard_unpack_set(
            in_file,
            output=True,
        )
        assert 'output' in meta
        assert 'testfile1' in meta['output']
