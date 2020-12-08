import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from plugins.unpacking.generic_carver.code.generic_carver import remove_false_positive_archives
from test.unit.unpacker.test_unpacker import TestUnpackerBase
from helperFunctions.file_system import get_test_data_dir

# pylint: disable=protected-access

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestGenericCarver(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('generic/carver', 'generic_carver')

    def test_extraction(self):
        in_file = '{}/generic_carver_test'.format(get_test_data_dir())
        files, meta_data = self.unpacker._extract_files_from_file_using_specific_unpacker(in_file, self.tmp_dir.name, self.unpacker.unpacker_plugins['generic/carver'])
        files = set(files)
        self.assertEqual(len(files), 1, 'file number incorrect')
        self.assertEqual(files, {'{}/64.zip'.format(self.tmp_dir.name)}, 'not all files found')
        self.assertIn('output', meta_data)
        self.assertIn('screening', meta_data)


def test_remove_false_positives_zip():
    with TemporaryDirectory() as temp_dir:
        test_file_zip = Path(temp_dir) / '_fake_zip.zip.extracted' / 'fake_zip.zip'
        os.mkdir(test_file_zip.parent)
        shutil.copyfile(TEST_DATA_DIR / 'fake_zip.zip', test_file_zip)
        remove_false_positive_archives('fake_zip.zip', temp_dir)
        assert test_file_zip.is_file() is False


def test_remove_false_positives_tar():
    with TemporaryDirectory() as temp_dir:
        test_file_tar = Path(temp_dir) / '_fake_tar.tar.extracted' / 'fake_tar.tar'
        os.mkdir(test_file_tar.parent)
        shutil.copyfile(TEST_DATA_DIR / 'fake_tar.tar', test_file_tar)
        remove_false_positive_archives('fake_tar.tar', temp_dir)
        assert test_file_tar.is_file() is False


def test_remove_false_positives_7z():
    with TemporaryDirectory() as temp_dir:
        test_file_7z = Path(temp_dir) / '_fake_7z.7z.extracted' / 'fake_7z.7z'
        os.mkdir(test_file_7z.parent)
        shutil.copyfile(TEST_DATA_DIR / 'fake_7z.7z', test_file_7z)
        remove_false_positive_archives('fake_7z.7z', temp_dir)
        assert test_file_7z.is_file() is False
