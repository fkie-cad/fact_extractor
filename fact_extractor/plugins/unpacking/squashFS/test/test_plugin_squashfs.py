from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from test.unit.unpacker.test_unpacker import TestUnpackerBase

from ..code.squash_fs import unpack_function

TEST_DATA_DIR = Path(__file__).parent / 'data'


def test_not_unpackable_file():
    empty_test_file = TEST_DATA_DIR / 'empty'
    with TemporaryDirectory(prefix='fact_test_') as unpack_dir, pytest.raises(ValueError, match='not a SquashFS file'):
        unpack_function(empty_test_file, unpack_dir)


class TestSquashUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('filesystem/squashfs', 'SquashFS')

    @pytest.mark.parametrize(
        'file',
        [
            ('avm_be.sqfs4',),
            ('avm_le.sqfs4',),
            ('gzip.sqfs',),
            ('lz4.sqfs',),
            ('lzma.sqfs',),
            ('lzma1_be.sqfs3',),
            ('lzma1_le.sqfs3',),
            ('lzma_be.sqfs2',),
            ('lzma_le.sqfs2',),
            ('lzo.sqfs',),
            ('xz.sqfs',),
            ('zlib_be.sqfs3',),
            ('zlib_le.sqfs3',),
            ('zstd.sqfs',),
            # non-standard magic
            ('test.sqlz',),
            ('test.zlqs',),
            ('test.hsqt',),
            ('test.tqsh',),
            ('test.qshs',),
            ('test.shsq',),
        ],
    )
    def test_extraction_sqfs(self, file):
        meta_data = self.check_unpacking_of_standard_unpack_set(TEST_DATA_DIR / file)
        assert meta_data['plugin_used'] == 'SquashFS'
        assert 'Number of inodes 5' in meta_data['output']
