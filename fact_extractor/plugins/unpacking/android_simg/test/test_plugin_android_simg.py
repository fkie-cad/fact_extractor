import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(root_dir))

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestAndroidSimgUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('filesystem/android-simg', 'Android-sparse-image')

    def test_extraction_simg(self):
        in_file = TEST_DATA_DIR / 'simg.img'
        files, _ = self.unpacker.extract_files_from_file(str(in_file), self.tmp_dir.name)
        assert len(files) == 1
        assert files[0].endswith('raw')
