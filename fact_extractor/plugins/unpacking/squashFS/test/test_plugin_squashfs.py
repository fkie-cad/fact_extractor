from pathlib import Path
import pytest
from tempfile import TemporaryDirectory

from test.unit.unpacker.test_unpacker import TestUnpackerBase

from ..code.squash_fs import _unpack_success, unpack_function, SQUASH_UNPACKER

TEST_DATA_DIR = Path(__file__).parent / 'data'


@pytest.mark.parametrize(
    'unpack_path, expected',
    [
        ('/foo/bar/unpacker', False),
        (TEST_DATA_DIR, True),
    ],
)
def test_unpack_success(unpack_path, expected):
    assert _unpack_success(unpack_path) == expected


def test_not_unpackable_file():
    empty_test_file = TEST_DATA_DIR / 'empty'
    with TemporaryDirectory(prefix='fact_test_') as unpack_dir:
        result = unpack_function(empty_test_file, unpack_dir)
    assert 'sasquatch - error' in result
    assert 'unsquashfs4-avm-be - error' in result


def test_tool_paths_set_correctly():
    for unpacker, _ in SQUASH_UNPACKER:
        assert unpacker.exists(), f'{unpacker} not found.'


class TestSquashUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('filesystem/squashfs', 'SquashFS')

    def test_extraction_sqfs(self):
        self.check_unpacking_of_standard_unpack_set(
            TEST_DATA_DIR / 'sqfs.img', additional_prefix_folder='fact_extracted'
        )
