import zipfile
from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestUntrxUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/trx', 'untrx')

    def test_extraction_trx(self):
        files, _ = self.unpacker.extract_files_from_file(TEST_DATA_DIR / 'trx.img', self.tmp_dir.name)
        assert len(files) == 1
        with zipfile.ZipFile(files[0], 'r') as extracted_file:
            included_file_list = [name for f in extracted_file.namelist() if (name := Path(f).name)]
            for file in ['test file 3_.txt', 'testfile1', 'testfile2']:
                assert file in included_file_list
