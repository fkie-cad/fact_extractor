import os

import pytest

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestPaToolUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('application/vnd.ms-cab-compressed', 'PaTool')
        self.check_unpacker_selection('application/x-lzh-compressed', 'PaTool')

    @pytest.mark.parametrize(
        'in_file, ignore',
        [
            ('test.a', {'data'}),
            ('test.cab', None),
            ('test.jar', {'MANIFEST.MF'}),
            ('test.lha', None),
            ('test.tar.bz2', None),
            ('test.tar.gz', None),
            ('test.tar.zip', None),
            ('test.zoo', None),
        ],
    )
    def test_extraction(self, in_file, ignore):
        self.check_unpacking_of_standard_unpack_set(
            os.path.join(TEST_DATA_DIR, in_file),
            additional_prefix_folder='get_files_test',
            output=False,
            ignore=ignore,
        )
