import os
from pathlib import Path
from tempfile import TemporaryDirectory

from helperFunctions.file_system import get_test_data_dir
from plugins.unpacking.microtik.code.npk import unpack_function
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestNpk(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/microtic-npk', 'Micotic NPK files')

    @staticmethod
    def test_extraction_bad_file():
        file_path = str(Path(get_test_data_dir(), 'test_data_file.bin'))

        with TemporaryDirectory() as tmp_dir:
            meta_data = unpack_function(file_path, tmp_dir)

        assert 'Invalid' in meta_data['error']
