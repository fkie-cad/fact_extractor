from pathlib import Path
from fact_extractor.helperFunctions.hash import get_sha256
from common_helper_files import get_binary_from_file
from fact_extractor.test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestDraytekVigor167Unpacker(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/draytek-vigor-167', 'Draytek Vigor 167')

    def test_extraction_valid_image(self):
        test_file = Path(TEST_DATA_DIR, 'valid_draytekvigor167_image.bin')
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(test_file, self.tmp_dir.name)

        assert meta_data['output'] == 'successfully unpacked image'
        assert len(unpacked_files) == 2, 'number of extracted files not correct'
        assert str(Path(self.tmp_dir.name) / 'kernel_image') in unpacked_files, 'kernel image not extracted'
        assert str(Path(self.tmp_dir.name) / 'squashfs_root') in unpacked_files, 'squashfs not extracted'
        squashfs_binary = get_binary_from_file(Path(self.tmp_dir.name) / 'squashfs_root')
        squashfs_hash = get_sha256(squashfs_binary)
        assert squashfs_hash == '73b648f484ab0a34ce00729ce8b7ef183885b4b5c540344a8451d18fe94cc2fa'

    def test_extraction_invalid_image(self):
        test_file = Path(TEST_DATA_DIR, 'invalid_draytekvigor167_image_struct_error.bin')
        _, meta_data = self.unpacker.extract_files_from_file(test_file, self.tmp_dir.name)

        assert 'failed to recognize firmware container' in meta_data['output']
