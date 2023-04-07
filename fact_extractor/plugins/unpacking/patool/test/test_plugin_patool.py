import os

import pytest

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestPaToolUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('application/vnd.ms-cab-compressed', 'PaTool')

    @pytest.mark.parametrize(
        'in_file, ignore',
        [
            ('test.cab', None),
            ('test.tar.bz2', None),
            ('test.tar.zip', None),
        ],
    )
    def test_extraction(self, in_file, ignore):
        self.check_unpacking_of_standard_unpack_set(
            os.path.join(TEST_DATA_DIR, in_file),
            additional_prefix_folder='get_files_test',
            output=False,
            ignore=ignore,
        )

    def test_extract_deb(self):
        in_file = os.path.join(TEST_DATA_DIR, 'test.deb')
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        assert len(files) == 3, f'file number incorrect: {meta_data}'
        assert 'extracted to' in meta_data['output']
