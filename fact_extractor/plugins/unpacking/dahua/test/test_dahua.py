from pathlib import Path

from fact_extractor.test.unit.unpacker.test_unpacker import TestUnpackerBase


TEST_DATA_DIR = Path(Path(__file__).parent, 'data')


class TestDahuaUnpacker(TestUnpackerBase):

    def test_unpacker_selection(self):
        self.check_unpacker_selection('firmware/dahua', 'dahua')

    def test_extraction(self):
        input_file = Path(TEST_DATA_DIR, 'dh.bin')
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(str(input_file), self.tmp_dir.name)

        assert 'zip header fixed' in meta_data['output']
        assert len(unpacked_files) == 1
        assert f'{self.tmp_dir.name}/dahua_firmware.zip' in unpacked_files
        assert input_file.stat().st_size == Path(unpacked_files[0]).stat().st_size, 'file size should not change'
