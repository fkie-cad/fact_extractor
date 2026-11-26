from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestDraytekArsenalUnpacker(TestUnpackerBase):
    def test_unpacker_selection(self):
        self.check_unpacker_selection('firmware/draytek-rtos', 'draytek_arsenal')

    def test_extraction(self):
        input_file = TEST_DATA_DIR / 'test.rst'
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(input_file, self.tmp_dir.name)
        output_dir = Path(self.tmp_dir.name)

        assert meta_data['plugin_used'] == 'draytek_arsenal'
        assert meta_data['type'] == 'RTOS'
        assert meta_data['bin']['header']['size'] == '0x140'
        assert meta_data['bin']['header']['bootloader_version'] == 5
        assert meta_data['bin']['checksum'] == '0x12345678'
        assert meta_data['web']['checksum'] == '0x87654321'
        assert meta_data['ocurred_errors_while_unpacking'] == 'File has no dynamic kernel images\n'

        assert len(unpacked_files) == 3
        assert set(unpacked_files) == {
            str(output_dir / 'bootloader_and_rtos'),
            str(output_dir / 'web/index.htm'),
            str(output_dir / 'web/dir/file.txt'),
        }
        assert (output_dir / 'bootloader_and_rtos').read_bytes() == b'fake_bootloader!' + b'fake RTOS image\n' * 4
        assert (output_dir / 'web/index.htm').read_bytes() == b'<html>fake web content</html>\n'
        # files in the PFS can be LZ4 compressed themselves
        assert (output_dir / 'web/dir/file.txt').read_bytes() == b'compressed file content\n'

    def test_extraction_with_dlm(self):
        input_file = TEST_DATA_DIR / 'test_dlm.rst'
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(input_file, self.tmp_dir.name)
        output_dir = Path(self.tmp_dir.name)

        assert 'ocurred_errors_while_unpacking' not in meta_data
        assert len(unpacked_files) == 4
        assert str(output_dir / 'dlms') in unpacked_files
        assert (output_dir / 'dlms').read_bytes() == b'DLM/1.0fake encrypted DLM data\x00\x00'
