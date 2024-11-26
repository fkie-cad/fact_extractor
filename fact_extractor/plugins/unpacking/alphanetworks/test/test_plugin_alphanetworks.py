from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestAlphaNetworksUnpacker(TestUnpackerBase):
    def test_unpacker_selection(self):
        self.check_unpacker_selection('firmware/alphanetworks', 'alphanetworks')

    def test_extraction_normal(self):
        input_file = TEST_DATA_DIR / 'test_sample'
        assert input_file.is_file()
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(input_file, self.tmp_dir.name)
        assert meta_data['output']['base64 offset'] == 109
        assert meta_data['output']['inverted'] is False
        assert len(unpacked_files) == 3
        for file in ('script.sh', 'firmware.bin', 'ddPack.elf'):
            assert f'{self.tmp_dir.name}/{file}' in unpacked_files
        assert Path(f'{self.tmp_dir.name}/ddPack.elf').read_bytes().startswith(b'foobar')
        assert Path(f'{self.tmp_dir.name}/firmware.bin').read_bytes() == b'firmware_foobar\n'

    def test_extraction_inverted(self):
        input_file = TEST_DATA_DIR / 'test_sample_inverted'
        assert input_file.is_file()
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(input_file, self.tmp_dir.name)
        assert meta_data['output']['ddpack offset'] is None
        assert meta_data['output']['inverted'] is True
        assert len(unpacked_files) == 2
        for file in ('script.sh', 'firmware.bin'):
            assert f'{self.tmp_dir.name}/{file}' in unpacked_files
        assert Path(f'{self.tmp_dir.name}/firmware.bin').read_bytes().endswith(b'fw_foobar')
