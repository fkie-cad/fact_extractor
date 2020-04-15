import os
from test.unit.unpacker.test_unpacker import TestUnpackerBase


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestDlinkShrs(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/dlink-shrs', 'D-Link SHRS')

    def test_extraction(self):
        in_file = os.path.join(TEST_DATA_DIR, 'DIR867A1_FW120B10_Beta_for_security_issues_Stackoverflow_20191221.bin')
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        self.assertEqual(len(files), 1, 'decryption failed')
        self.assertIn('output', meta_data)
