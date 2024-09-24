import os
from pathlib import Path

import pytest
from common_helper_files import get_files_in_dir

from helperFunctions.file_system import (
    file_is_empty,
    file_name_sanitize,
    get_fact_bin_dir,
    get_src_dir,
    get_test_data_dir,
)


class TestFileSystemHelpers:
    def setup_method(self):
        self.current_cwd = os.getcwd()  # pylint: disable=attribute-defined-outside-init

    def teardown_method(self):
        os.chdir(self.current_cwd)

    @pytest.mark.parametrize('working_directory', [os.getcwd(), '/'])
    def test_check_correct_src_dir(self, working_directory):
        real_src_dir = get_src_dir()
        cwd = os.getcwd()
        try:
            os.chdir(working_directory)
            assert Path(f'{real_src_dir}/helperFunctions/file_system.py').is_file()
            assert get_src_dir() == real_src_dir, 'same source dir before and after chdir'
        finally:
            os.chdir(cwd)

    def test_get_fact_bin_dir(self):
        bin_dir = get_fact_bin_dir()
        files_in_bin_dir = [os.path.basename(f) for f in get_files_in_dir(bin_dir)]
        assert os.path.isdir(bin_dir)
        assert 'fact_extractor/bin' in bin_dir
        assert 'untrx' in files_in_bin_dir

    def test_file_is_zero(self):
        assert file_is_empty(f'{get_test_data_dir()}/zero_byte'), 'file is empty'
        assert not file_is_empty(f'{get_test_data_dir()}/get_files_test/testfile1'), 'file is not empty'
        assert not file_is_empty(os.path.join(get_test_data_dir(), 'broken_link')), 'Broken link is not empty'

    def test_sanitize_file_name(self):
        assert file_name_sanitize('../../../../a/b/c/d') == 'a/b/c/d', 'file was not sanitized'
        assert file_name_sanitize('dir/../../../../a/b/c/d') == 'dir/a/b/c/d', 'file was not sanitized'

    def test_file_is_zero_broken_link(self):
        assert not file_is_empty(os.path.join(get_test_data_dir(), 'broken_link')), 'Broken link is not empty'
