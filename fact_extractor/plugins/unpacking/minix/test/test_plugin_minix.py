from pathlib import Path

import pytest

from helperFunctions.file_system import decompress_test_file
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestMinixFsUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('filesystem/minix', 'minix')

    @pytest.mark.parametrize(
        'filename',
        [
            'minix_v1_be_namelen14.img.xz',
            'minix_v1_be_namelen30.img.xz',
            'minix_v1_le_namelen14.img.xz',
            'minix_v1_le_namelen30.img.xz',
            'minix_v2_be_namelen14.img.xz',
            'minix_v2_be_namelen30.img.xz',
            'minix_v2_le_namelen14.img.xz',
            'minix_v2_le_namelen30.img.xz',
            'minix_v3_be.img.xz',
            'minix_v3_le.img.xz',
        ],
    )
    def test_extraction_minix2(self, filename):
        path = TEST_DATA_DIR / filename
        assert path.is_file(), 'test file is missing'
        with decompress_test_file(path) as test_file:
            files, meta_data = self.unpacker.base.extract_files_from_file(str(test_file), self.tmp_dir.name)
            files = {p.name: p for f in files if (p := Path(f))}
            assert len(files) == 3, 'file number incorrect'
            assert sorted(files) == ['apple.txt', 'banana.txt', 'cherry.txt']
            assert files['apple.txt'].read_text() == 'apple\n'
