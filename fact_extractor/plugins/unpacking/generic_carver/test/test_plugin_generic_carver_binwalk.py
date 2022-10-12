from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase
from helperFunctions.file_system import get_test_data_dir

# pylint: disable=protected-access

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestGenericCarver(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('generic/carver', 'generic_carver')

    def test_extraction(self):
        in_file = f'{get_test_data_dir()}/generic_carver_test'
        files, meta_data = self.unpacker._extract_files_from_file_using_specific_unpacker(in_file, self.tmp_dir.name, self.unpacker.unpacker_plugins['generic/carver'])
        files = set(files)
        assert len(files) == 5, 'file number incorrect'
        assert str(Path(self.tmp_dir.name) / 'generic_carver_test_extract' / '0-100.unknown') in files, 'not all files found'
        assert 'output' in meta_data
