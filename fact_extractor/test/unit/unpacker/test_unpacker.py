import gc
import json
import os
import shutil
import unittest
from configparser import ConfigParser
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from helperFunctions.fileSystem import get_test_data_dir
from unpacker.unpack import Unpacker


class TestUnpackerBase(unittest.TestCase):
    def setUp(self):
        self.config = ConfigParser()
        self.ds_tmp_dir = TemporaryDirectory(prefix='faf_tests_')
        self.tmp_dir = TemporaryDirectory(prefix='faf_tests_')

        self.config.add_section('unpack')
        self.config.set('unpack', 'data_folder', self.ds_tmp_dir.name)
        self.config.set('unpack', 'blacklist', 'text/plain, image/png')
        self.config.add_section('ExpertSettings')
        self.config.set('ExpertSettings', 'header_overhead', '256')

        self.unpacker = Unpacker(config=self.config)
        os.makedirs(self.unpacker._report_folder, exist_ok=True)
        os.makedirs(self.unpacker._file_folder, exist_ok=True)

        self.test_file_path = Path(get_test_data_dir(), 'get_files_test/testfile1')

    def tearDown(self):
        self.ds_tmp_dir.cleanup()
        self.tmp_dir.cleanup()
        gc.collect()

    def get_unpacker_meta(self):
        return json.loads(Path(self.unpacker._report_folder, 'meta.json').read_text())

    def check_unpacker_selection(self, mime_type, plugin_name):
        name = self.unpacker.get_unpacker(mime_type)[1]
        self.assertEqual(name, plugin_name, 'wrong unpacker plugin selected')

    def check_unpacking_of_standard_unpack_set(self, in_file, additional_prefix_folder='', output=True):
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        files = set(files)
        self.assertEqual(len(files), 3, 'file number incorrect')
        self.assertEqual(files, {
            os.path.join(self.tmp_dir.name, additional_prefix_folder, 'testfile1'),
            os.path.join(self.tmp_dir.name, additional_prefix_folder, 'testfile2'),
            os.path.join(self.tmp_dir.name, additional_prefix_folder, 'generic folder/test file 3_.txt')
        }, 'not all files found')
        if output:
            self.assertIn('output', meta_data)
        return meta_data


class TestUnpackerCore(TestUnpackerBase):

    def test_generic_carver_found(self):
        self.assertTrue('generic/carver' in list(self.unpacker.unpacker_plugins.keys()), 'generic carver plugin not found')
        name = self.unpacker.unpacker_plugins['generic/carver'][1]
        self.assertEqual(name, 'generic_carver', 'generic_carver plugin not found')

    def test_unpacker_selection_unkown(self):
        self.check_unpacker_selection('unknown/blah', 'generic_carver')

    def test_unpacker_selection_whitelist(self):
        self.check_unpacker_selection('text/plain', 'NOP')
        self.check_unpacker_selection('image/png', 'NOP')

    @patch('unpacker.unpack.shutil.move', shutil.copy2)
    def test_generate_and_store_file_objects_zero_file(self):
        file_pathes = ['{}/zero_byte'.format(get_test_data_dir()), '{}/get_files_test/testfile1'.format(get_test_data_dir())]
        moved_files = self.unpacker.move_extracted_files(file_pathes, get_test_data_dir())

        self.assertEqual(len(moved_files), 1, 'number of objects not correct')
        self.assertEqual(moved_files[0].name, 'testfile1', 'wrong object created')
        self.assertIn('/get_files_test/testfile1', str(moved_files[0].absolute()))

    def test_unpack_failure_generic_carver_fallback(self):
        self.unpacker.GENERIC_CARVER_FALLBACK_BLACKLIST = []
        self._unpack_fallback_check('generic/carver', 'generic_carver')

    def test_unpack_failure_generic_fs_fallback(self):
        self.unpacker.GENERIC_FS_FALLBACK_CANDIDATES = ['7z']
        meta_data = self._unpack_fallback_check('generic/fs', 'generic_carver')
        self.assertIn('0_FALLBACK_genericFS', meta_data, 'generic FS Fallback entry missing')
        self.assertIn('0_ERROR_genericFS', meta_data, 'generic FS ERROR entry missing')

    def _unpack_fallback_check(self, fallback_mime, fallback_plugin_name):
        broken_zip = Path(get_test_data_dir(), 'container/broken.zip')
        self.unpacker.unpack(broken_zip)
        meta_data = self.get_unpacker_meta()

        self.assertEqual(meta_data['0_ERROR_7z'][0:6], '\n7-Zip')
        self.assertEqual(meta_data['0_FALLBACK_7z'], '7z (failed) -> {} (fallback)'.format(fallback_mime))
        self.assertEqual(meta_data['plugin_used'], fallback_plugin_name)

        return meta_data


class TestUnpackerCoreMain(TestUnpackerBase):

    def main_unpack_check(self, file_path, number_unpacked_files, first_unpacker):
        extracted_files = self.unpacker.unpack(file_path)
        meta_data = self.get_unpacker_meta()

        self.assertEqual(len(extracted_files), number_unpacked_files, 'not all files found')
        self.assertEqual(meta_data['plugin_used'], first_unpacker, 'Wrong plugin in Meta')
        self.assertEqual(meta_data['number_of_unpacked_files'], number_unpacked_files, 'Number of unpacked files wrong in Meta')

    def test_main_unpack_function(self):
        test_file_path = Path(get_test_data_dir(), 'container/test.zip')
        self.main_unpack_check(test_file_path, 3, '7z')
