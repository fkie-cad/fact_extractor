import os
import unittest

from common_helper_files import get_files_in_dir
from helperFunctions.fileSystem import (
    file_is_empty, get_faf_bin_dir, get_parent_dir, get_src_dir,
    get_test_data_dir
)


class TestFileSystemHelpers(unittest.TestCase):

    def setUp(self):
        self.current_cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.current_cwd)

    def test_get_parent_dir(self):
        self.assertEqual(get_parent_dir('/foo/bar/test'), '/foo/bar', 'parent directory')

    def check_correct_src_dir(self, working_directory):
        real_src_dir = get_src_dir()
        os.chdir(working_directory)
        self.assertTrue(os.path.exists('{}/helperFunctions/fileSystem.py'.format(real_src_dir)), 'fileSystem.py found in correct place')
        self.assertEqual(get_src_dir(), real_src_dir, 'same source dir before and after chdir')

    def test_get_src_dir_cwd(self):
        self.check_correct_src_dir(os.getcwd())

    def test_get_src_dir_root(self):
        self.check_correct_src_dir('/')

    def test_get_faf_bin_dir(self):
        bin_dir = get_faf_bin_dir()
        files_in_bin_dir = [os.path.basename(f) for f in get_files_in_dir(bin_dir)]
        self.assertTrue(os.path.isdir(bin_dir))
        self.assertIn('fact_extractor/bin', bin_dir)
        self.assertIn('untrx', files_in_bin_dir)

    def test_file_is_zero(self):
        self.assertTrue(file_is_empty('{}/zero_byte'.format(get_test_data_dir())), 'file is empty but stated differently')
        self.assertFalse(file_is_empty('{}/get_files_test/testfile1'.format(get_test_data_dir())), 'file not empty but stated differently')
        self.assertFalse(file_is_empty(os.path.join(get_test_data_dir(), 'broken_link')), 'Broken link is not empty')

    def test_file_is_zero_broken_link(self):
        self.assertFalse(file_is_empty(os.path.join(get_test_data_dir(), 'broken_link')), 'Broken link is not empty')
