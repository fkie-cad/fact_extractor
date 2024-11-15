from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from helperFunctions.hash import get_sha256
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestPaToolUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('application/vnd.ms-cab-compressed', 'PaTool')
        self.check_unpacker_selection('application/x-lzh-compressed', 'PaTool')

    @pytest.mark.parametrize(
        ('in_file', 'ignore'),
        [
            ('test.cab', None),
            ('test.cpio', None),
            ('test.jar', {'MANIFEST.MF'}),
            ('test.lha', None),
            ('test.shar', None),
            ('test.tar.Z', None),
            ('test.tar.bz2', None),
            ('test.tar.gz', None),
            ('test.tar.lz', None),
            ('test.tar.xz', None),
            ('test.tar.zip', None),
            ('test.zoo', None),
            ('test.zpaq', None),
        ],
    )
    def test_archive_extraction(self, in_file, ignore):
        self.check_unpacking_of_standard_unpack_set(
            TEST_DATA_DIR / in_file,
            additional_prefix_folder='get_files_test',
            output=False,
            ignore=ignore,
        )

    @pytest.mark.parametrize(
        'in_file',
        [
            'test.a',
            'test.bz2',
            'test.gz',
            'test.lrz',
            'test.lz',
            'test.lz4',
            'test.lzo',
            'test.rz',
            'test.xz',
        ],
    )
    def test_file_extraction(self, in_file):
        files, meta = self.unpacker.extract_files_from_file(TEST_DATA_DIR / in_file, self.tmp_dir.name)
        assert len(files) == 1, f'unpacking of {in_file} unsuccessful: {meta}'
        assert meta['plugin_used'] == 'PaTool'
        assert get_sha256(Path(files[0]).read_bytes()).startswith('deadc0de')

    def test_extraction_arc(self):
        """
        special case arc: arguments (i.e. paths) and names of packed files must not be too long.
        Unfortunately, the name of the third test file as well as the path of the test folder are too long.
        """
        with TemporaryDirectory() as tmp_dir:
            target_file = Path(tmp_dir) / 'test.arc'
            target_file.write_bytes((TEST_DATA_DIR / 'test.arc').read_bytes())
            files, _ = self.unpacker.extract_files_from_file(target_file, self.tmp_dir.name)
        assert len(files) == 2
        unpacked_files = sorted(Path(f).name for f in files)
        assert unpacked_files == ['testfile1', 'testfile2']

    def test_extract_deb(self):
        test_file = TEST_DATA_DIR / 'test.deb'
        files, meta_data = self.unpacker.extract_files_from_file(test_file, self.tmp_dir.name)
        assert len(files) == 3, f'file number incorrect: {meta_data}'
        assert 'extracted to' in meta_data['output']
