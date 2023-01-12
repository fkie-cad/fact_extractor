import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest

from plugins.unpacking.generic_carver.code.generic_carver import ArchivesFilter
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
        assert len(files) == 1, 'file number incorrect'
        assert files == {f'{self.tmp_dir.name}/64.zip'}, 'not all files found'
        assert 'output' in meta_data
        assert 'filter_log' in meta_data

    def test_extraction_of_filtered_files(self):
        in_file = str(TEST_DATA_DIR / 'fake_xz.bin')
        files, meta_data = self.unpacker._extract_files_from_file_using_specific_unpacker(in_file, self.tmp_dir.name, self.unpacker.unpacker_plugins['generic/carver'])
        assert len(files) == 0
        assert 'was removed' in meta_data['filter_log']


@pytest.mark.parametrize('filename', ['fake_zip.zip', 'fake_tar.tar', 'fake_7z.7z', 'fake_xz.xz', 'fake_gz.gz'])
def test_remove_false_positives(filename):
    with TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / filename
        shutil.copyfile(TEST_DATA_DIR / filename, test_file)
        ArchivesFilter(temp_dir).remove_false_positive_archives()
        assert test_file.is_file() is False


def test_remove_trailing_data():
    filename = 'trailing_data.zip'
    with TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / filename
        source_file = TEST_DATA_DIR / filename
        shutil.copyfile(source_file, test_file)
        arch_filter = ArchivesFilter(temp_dir)
        arch_filter._remove_trailing_data_7z(test_file)

        assert arch_filter.screening_logs == ['Removed trailing data at the end of trailing_data.zip']
        assert test_file.stat().st_size < source_file.stat().st_size
