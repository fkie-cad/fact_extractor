# pylint: disable=attribute-defined-outside-init

from __future__ import annotations

import gc
import json
import shutil
from configparser import ConfigParser
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from helperFunctions.file_system import get_test_data_dir
from unpacker.unpack import Unpacker


class TestUnpackerBase:
    def setup_method(self):
        self.config = ConfigParser()
        self.ds_tmp_dir = TemporaryDirectory(prefix='fact_tests_')
        self.tmp_dir = TemporaryDirectory(prefix='fact_tests_')

        self.config.add_section('unpack')
        self.config.set('unpack', 'data_folder', self.ds_tmp_dir.name)
        self.config.set('unpack', 'blacklist', 'text/plain, image/png')
        self.config.add_section('ExpertSettings')
        self.config.set('ExpertSettings', 'header_overhead', '256')
        self.config.set('ExpertSettings', 'unpack_threshold', '0.8')

        self.unpacker = Unpacker(config=self.config)
        self.unpacker._report_folder.mkdir(exist_ok=True)
        self.unpacker._file_folder.mkdir(exist_ok=True)

        self.test_file_path = Path(get_test_data_dir(), 'get_files_test/testfile1')

    def teardown_method(self):
        self.ds_tmp_dir.cleanup()
        self.tmp_dir.cleanup()
        gc.collect()

    def get_unpacker_meta(self):
        return json.loads(
            Path(self.unpacker._report_folder, 'meta.json').read_text()  # pylint: disable=protected-access
        )

    def check_unpacker_selection(self, mime_type, plugin_name):
        name = self.unpacker.base.get_unpacker(mime_type)[1]
        assert name == plugin_name, 'wrong unpacker plugin selected'

    def check_unpacking_of_standard_unpack_set(
        self,
        in_file: Path | str,
        additional_prefix_folder: str = '',
        output: bool = True,
        ignore: set[str] | None = None,
        trailing_data: bool = False,
    ):
        files, meta_data = self.unpacker.base.extract_files_from_file(str(in_file), self.tmp_dir.name)
        files = {f for f in files if not any(rule in f for rule in ignore or set())}
        assert len(files) == 3 if not trailing_data else 4, f'file number incorrect: {meta_data}'
        expected_files = ['testfile1', 'testfile2', 'generic folder/test file 3_.txt']
        if trailing_data:
            expected_files.append('trailing.bin')
        for path in expected_files:
            assert (
                str(Path(self.tmp_dir.name, additional_prefix_folder, path)) in files
            ), f'file {path} missing from unpacked files'
        if output:
            assert 'output' in meta_data
        if trailing_data:
            assert 'trailing_data' in meta_data
        return meta_data


class TestUnpackerCore(TestUnpackerBase):
    def test_generic_carver_found(self):
        assert 'generic/carver' in list(self.unpacker.base.unpacker_plugins), 'generic carver plugin not found'
        name = self.unpacker.base.unpacker_plugins['generic/carver'][1]
        assert name == 'generic_carver', 'generic_carver plugin not found'

    def test_unpacker_selection_unknown(self):
        self.check_unpacker_selection('unknown/blah', 'generic_carver')

    def test_unpacker_selection_whitelist(self):
        self.check_unpacker_selection('text/plain', 'NOP')
        self.check_unpacker_selection('image/png', 'NOP')

    @patch('unpacker.unpack.shutil.move', shutil.copy2)
    def test_generate_and_store_file_objects_zero_file(self):
        file_paths = [f'{get_test_data_dir()}/zero_byte', f'{get_test_data_dir()}/get_files_test/testfile1']
        moved_files = self.unpacker.move_extracted_files(file_paths, get_test_data_dir())

        assert len(moved_files) == 1, 'number of objects not correct'
        assert moved_files[0].name == 'testfile1', 'wrong object created'
        assert '/get_files_test/testfile1' in str(moved_files[0].absolute())

    @patch('unpacker.unpack.shutil.move', shutil.copy2)
    def test_extract_everything(self):
        self.unpacker.extract_everything = True
        file_paths = [f'{get_test_data_dir()}/zero_byte', f'{get_test_data_dir()}/get_files_test/testfile1']
        moved_files = self.unpacker.move_extracted_files(file_paths, get_test_data_dir())
        moved_files.sort()

        assert len(moved_files) == 2, 'number of objects not correct'
        assert moved_files[1].name == 'zero_byte', 'empty files should not be discarded'

    @patch('unpacker.unpack.shutil.move')
    def test_move_extracted_files(self, mock_shutil):  # pylint: disable=unused-argument
        file_paths = [f'{get_test_data_dir()}/fake_file', f'{get_test_data_dir()}/get_files_test/testfile1']
        moved_files = self.unpacker.move_extracted_files(file_paths, get_test_data_dir())

        assert len(moved_files) == 2, 'number of objects not correct'
        assert moved_files[1].name == 'testfile1', 'wrong object created'
        assert '/get_files_test/testfile1' in str(moved_files[1].absolute())

    @patch('unpacker.unpack.shutil.move')
    def test_move_extracted_files_raise_assert(self, mock_shutil):
        file_paths = [f'{get_test_data_dir()}/fake_file', f'{get_test_data_dir()}/get_files_test/testfile1']
        # Raise exception once, so fake_file shouldn't exist is the returned moved_files
        mock_shutil.side_effect = [OSError('File exists'), '']

        moved_files = self.unpacker.move_extracted_files(file_paths, get_test_data_dir())

        assert len(moved_files) == 1, 'number of objects not correct'
        assert moved_files[0].name == 'testfile1', 'wrong object created'
        assert '/get_files_test/testfile1' in str(moved_files[0].absolute())

    def test_clean_up(self):
        temp_dir = Mock()
        self.unpacker.cleanup(temp_dir)
        temp_dir.cleanup.assert_called()

        temp_dir.cleanup.side_effect = OSError('some error')
        self.unpacker.cleanup(temp_dir)

    def test_unpack_failure_generic_carver_fallback(self):
        self.unpacker.CARVER_FALLBACK_BLACKLIST = []
        self._unpack_fallback_check('generic/carver', 'generic_carver')

    def test_unpack_failure_generic_fs_fallback(self):
        self.unpacker.FS_FALLBACK_CANDIDATES = ['7z']
        meta_data = self._unpack_fallback_check('generic/fs', 'generic_carver')
        assert '0_FALLBACK_genericFS' in meta_data, 'generic FS Fallback entry missing'
        assert '0_ERROR_genericFS' in meta_data, 'generic FS ERROR entry missing'

    def _unpack_fallback_check(self, fallback_mime, fallback_plugin_name):
        broken_zip = Path(get_test_data_dir(), 'container/broken.zip')
        self.unpacker.unpack(broken_zip)
        meta_data = self.get_unpacker_meta()

        assert meta_data['0_ERROR_7z'][0:6] == '\n7-Zip'
        assert meta_data['0_FALLBACK_7z'] == f'7z (failed) -> {fallback_mime} (fallback)'
        assert meta_data['plugin_used'] == fallback_plugin_name

        return meta_data


class TestUnpackerCoreMain(TestUnpackerBase):
    def main_unpack_check(self, file_path, number_unpacked_files, number_of_excluded_files, first_unpacker):
        extracted_files = self.unpacker.unpack(file_path)
        meta_data = self.get_unpacker_meta()

        assert len(extracted_files) == number_unpacked_files, 'not all files found'
        assert meta_data['plugin_used'] == first_unpacker, 'Wrong plugin in Meta'
        assert meta_data['number_of_unpacked_files'] == number_unpacked_files, 'Number of unpacked files wrong in Meta'
        assert (
            meta_data['number_of_excluded_files'] == number_of_excluded_files
        ), 'Number of excluded files wrong in Meta'

    def test_main_unpack_function(self):
        test_file_path = Path(get_test_data_dir(), 'container/test.zip')
        self.main_unpack_check(test_file_path, 3, 0, '7z')

    def test_main_unpack_exclude_archive(self):
        test_file_path = Path(get_test_data_dir(), 'container/test.zip')
        self.unpacker.base.exclude = ['*test.zip']
        self.main_unpack_check(test_file_path, 0, 1, None)

    def test_main_unpack_exclude_subdirectory(self):
        test_file_path = Path(get_test_data_dir(), 'container/test.zip')
        self.unpacker.base.exclude = ['*/generic folder/*']
        self.main_unpack_check(test_file_path, 2, 1, '7z')

    def test_main_unpack_exclude_files(self):
        test_file_path = Path(get_test_data_dir(), 'container/test.zip')
        self.unpacker.base.exclude = ['*/get_files_test/*test*']
        self.main_unpack_check(test_file_path, 0, 3, '7z')
