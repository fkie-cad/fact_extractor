from pathlib import Path
from helperFunctions.hash import get_sha256
from common_helper_files import get_binary_from_file
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestDraytekVigor167Unpacker(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/draytek-vigor-167', 'Draytek Vigor 167')

    def test_extraction(self):
        test_file = Path(TEST_DATA_DIR, 'valid_draytekvigor167_image.bin')
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(test_file, self.tmp_dir.name)

        self.assertEqual(meta_data['output'], 'successfully unpacked image')
        self.assertEqual(len(unpacked_files), 2, 'number of extracted files not correct')
        self.assertEqual(unpacked_files[0], str(Path(self.tmp_dir.name) / 'kernel_image'), 'file name not correct')
        self.assertEqual(unpacked_files[1], str(Path(self.tmp_dir.name) / 'squashfs_root'), 'file name not correct')
        squashfs_binary = get_binary_from_file(unpacked_files[1])
        squashfs_hash = get_sha256(squashfs_binary)
        self.assertEqual(squashfs_hash, '73b648f484ab0a34ce00729ce8b7ef183885b4b5c540344a8451d18fe94cc2fa')

        test_file = Path(TEST_DATA_DIR, 'invalid_draytekvigor167_image_struct_error.bin')
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(test_file, self.tmp_dir.name)

        self.assertIn('failed to recognize firmware container', meta_data['output'])
