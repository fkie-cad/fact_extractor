import os
from tempfile import TemporaryDirectory
import pytest

from test.unit.unpacker.test_unpacker import TestUnpackerBase  # pylint: disable=wrong-import-order

from ..code.squash_fs import _get_unpacker_name, _unpack_success, unpack_function


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


@pytest.mark.parametrize('unpacker_path, expected', [
    ('/foo/bar/unpacker', 'unpacker'),
    ('unpacker', 'unpacker'),
])
def test_get_unpacker_name(unpacker_path, expected):
    assert _get_unpacker_name(unpacker_path) == expected


@pytest.mark.parametrize('unpack_path, expected', [
    ('/foo/bar/unpacker', False),
    (TEST_DATA_DIR, True),
])
def test_unpack_success(unpack_path, expected):
    assert _unpack_success(unpack_path) == expected


def test_not_unpackable_file():
    with pytest.raises(Exception):
        empty_test_file = os.path.join(TEST_DATA_DIR, 'empty')
        unpack_dir = TemporaryDirectory(prefix='fact_test_')
        _ = unpack_function(empty_test_file, unpack_dir)



class TestSquashUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('filesystem/squashfs', 'SquashFS')

    def test_extraction_sqfs(self):
        self.check_unpacking_of_standard_unpack_set(os.path.join(TEST_DATA_DIR, 'sqfs.img'), additional_prefix_folder='fact_extracted')
