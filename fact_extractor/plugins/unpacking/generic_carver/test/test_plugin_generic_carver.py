import re
import zlib
from pathlib import Path

import pytest

from helperFunctions.file_system import get_test_data_dir
from plugins.unpacking.generic_carver.code.generic_carver import unpack_function
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestGenericCarver(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('generic/carver', 'generic_carver')

    def test_extraction(self):
        in_file = Path(get_test_data_dir()) / 'generic_carver_test'
        files, meta_data = self.unpacker.base._extract_files_from_file_using_specific_unpacker(
            in_file, self.tmp_dir.name, self.unpacker.base.unpacker_plugins['generic/carver']
        )
        files = set(files)
        assert len(files) == 3, 'file number incorrect'
        assert f'{self.tmp_dir.name}/100-887.zip' in files, 'hidden zip not identified correctly'
        assert 'output' in meta_data

    def test_zlib_carving(self):
        in_file = TEST_DATA_DIR / 'zlib_carving_test'
        files, meta_data = self.unpacker.base._extract_files_from_file_using_specific_unpacker(
            in_file, self.tmp_dir.name, self.unpacker.base.unpacker_plugins['generic/carver']
        )
        assert len(files) == 9, 'file number incorrect'
        assert sum(1 if f.endswith('.zlib_carver') else 0 for f in files), 'wrong number of carved zlib streams'
        zlib_file_1 = sorted(files)[1]
        content = zlib.decompress(Path(zlib_file_1).read_bytes())
        assert b'test file' in content, 'test file not carved correctly'

    def test_filter(self):
        in_file = TEST_DATA_DIR / 'carving_test_file'
        assert Path(in_file).is_file()
        files, meta_data = self.unpacker.base._extract_files_from_file_using_specific_unpacker(
            in_file, self.tmp_dir.name, self.unpacker.base.unpacker_plugins['generic/carver']
        )
        files = set(files)
        assert len(files) == 4, 'file number incorrect'
        assert 'removed chunk 300-428' in meta_data['output']
        for file in ('0-128.unknown', '128-300.zip', '428-562.sevenzip', '562-626.unknown'):
            assert f'{self.tmp_dir.name}/{file}' in files

    @pytest.mark.parametrize('file_format', ['7z', 'gz', 'tar', 'xz', 'zip'])
    def test_fake_archives(self, file_format):
        in_file = TEST_DATA_DIR / f'fake_{file_format}.{file_format}'
        assert Path(in_file).is_file()
        meta = unpack_function(str(in_file), self.tmp_dir.name)
        assert meta == {'output': 'No valid chunks found.'}

    @pytest.mark.parametrize(('file_format', 'expected_size'), [('bz2', 52), ('zip', 170)])
    def test_trailing_data(self, file_format, expected_size):
        in_file = Path(get_test_data_dir()) / f'trailing_data.{file_format}'
        assert Path(in_file).is_file()
        meta = unpack_function(str(in_file), self.tmp_dir.name)
        carved_size = int(re.search(r'size: (\d+)', meta['output']).group(1))
        assert carved_size == expected_size
