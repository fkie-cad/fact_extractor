import os

from test.unit.unpacker.test_unpacker import TestUnpackerBase


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestUBootUnpacker(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/u-boot', 'Uboot')

    def test_extraction(self):
        test_file_path = os.path.join(TEST_DATA_DIR, 'uboot.image_with_header')
        extracted_files, meta_data = self.unpacker.extract_files_from_file(test_file_path, self.tmp_dir.name)

        assert meta_data['plugin_used'] == 'Uboot', 'wrong plugin applied'

        assert len(extracted_files) == 3, 'not all files extracted'
        assert any('uboot.lzma' in extracted_file for extracted_file in extracted_files), 'main container not extracted'

    def test_extraction_dtb(self):
        test_file_path = os.path.join(TEST_DATA_DIR, 'uboot.dtb')
        extracted_files, meta_data = self.unpacker.extract_files_from_file(test_file_path, self.tmp_dir.name)

        assert meta_data['plugin_used'] == 'Uboot', 'wrong plugin applied'

        assert len(extracted_files) == 4, 'not all files extracted'
        assert any(f.endswith('.dtb') for f in extracted_files), 'dtb not extracted'
        assert 'extract-dtb' in meta_data
        assert 'Dumped 01_dtbdump_Manufac_XYZ1234ABC.dtb' in meta_data['extract-dtb']
