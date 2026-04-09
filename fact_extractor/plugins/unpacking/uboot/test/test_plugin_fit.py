from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'

EXPECTED_FILE_COUNT = 3


class TestFITUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('linux/device-tree', 'FIT')

    def test_extraction_itb(self):
        test_file_path = Path(TEST_DATA_DIR) / 'fit.itb'
        extracted_files, meta_data = self.unpacker.extract_files_from_file(str(test_file_path), self.tmp_dir.name)

        assert meta_data['plugin_used'] == 'FIT', 'wrong plugin applied'
        assert meta_data.get('error') is None
        assert meta_data.get('output') is not None

        assert len(extracted_files) == EXPECTED_FILE_COUNT, 'not all files extracted'
        for element in extracted_files:
            assert Path(element).name in ['kernel.bin', 'fdt.bin', 'rootfs.bin']

    def test_extraction_dtb(self):
        test_file_path = Path(TEST_DATA_DIR) / 'test.dtb'
        extracted_files, meta_data = self.unpacker.extract_files_from_file(str(test_file_path), self.tmp_dir.name)

        assert meta_data['plugin_used'] == 'FIT', 'wrong plugin applied'
        assert meta_data.get('error') is None
        assert meta_data.get('output') is not None

        files = {p.name: p for f in extracted_files if (p := Path(f))}
        assert 'kernel.bin' in files
        assert files['kernel.bin'].read_bytes() == b'Hello'
        assert 'ramdisk.bin' in files
        assert files['ramdisk.bin'].read_bytes() == b'World', 'decompression failed'
        assert 'nested.bin' in files
        assert files['nested.bin'].read_bytes() == b'Nested', 'nested file not extracted'
        assert 'unpacked data from node images/ramdisk/nested (6 bytes)' in meta_data['output']
