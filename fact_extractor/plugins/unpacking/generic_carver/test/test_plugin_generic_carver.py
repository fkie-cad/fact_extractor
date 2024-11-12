from pathlib import Path

from helperFunctions.file_system import get_test_data_dir
from test.unit.unpacker.test_unpacker import TestUnpackerBase

# pylint: disable=protected-access

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestGenericCarver(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('generic/carver', 'generic_carver')

    def test_extraction(self):
        in_file = f'{get_test_data_dir()}/generic_carver_test'
        files, meta_data = self.unpacker._extract_files_from_file_using_specific_unpacker(
            in_file, self.tmp_dir.name, self.unpacker.unpacker_plugins['generic/carver']
        )
        files = set(files)
        assert len(files) == 3, 'file number incorrect'  # noqa: PLR2004
        assert f'{self.tmp_dir.name}/100-887.zip' in files, 'hidden zip not identified correctly'
        assert 'output' in meta_data

    def test_filter(self):
        in_file = TEST_DATA_DIR / 'carving_test_file'
        assert Path(in_file).is_file()
        files, meta_data = self.unpacker._extract_files_from_file_using_specific_unpacker(
            str(in_file), self.tmp_dir.name, self.unpacker.unpacker_plugins['generic/carver']
        )
        files = set(files)
        assert len(files) == 4, 'file number incorrect'  # noqa: PLR2004
        assert 'removed chunk 300-428' in meta_data['output']
        for file in ('0-128.unknown', '128-300.zip', '428-562.sevenzip', '562-626.unknown'):
            assert f'{self.tmp_dir.name}/{file}' in files
