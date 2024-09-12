import os

from common_helper_files import get_binary_from_file

from fact_extractor.helperFunctions.hash import get_sha256
from fact_extractor.test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestUnpackerPluginZlib(TestUnpackerBase):

    def test_unpacker_selection(self):
        self.check_unpacker_selection('compression/zlib', 'Zlib')

    def test_extraction(self):
        in_file = os.path.join(TEST_DATA_DIR, 'test.zlib')
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        assert len(files) == 1, 'number of extracted files not correct'
        assert files[0] == os.path.join(self.tmp_dir.name, 'zlib_decompressed'), 'file name not correct'
        file_binary = get_binary_from_file(files[0])
        file_hash = get_sha256(file_binary)
        assert file_hash == 'e429103649e24ca126077bfb38cce8c57cc913a966d7e36356e4fe0513ab02c4'
        assert len(meta_data.keys()) == 4, 'more or fewer than standard keys in meta dict'
