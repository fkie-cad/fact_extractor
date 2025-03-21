from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestDLinkEncImg(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/dlink-encrpted-img', 'D-Link encrpted_img')

    def test_extraction(self):
        in_file = TEST_DATA_DIR / 'testfile.encrpted_img'
        files, meta_data = self.unpacker.extract_files_from_file(in_file, self.tmp_dir.name)
        assert len(files) == 1
        assert 'output' in meta_data
        assert meta_data['plugin_used'] == 'D-Link encrpted_img'
        assert 'Decrypted image' in meta_data['output']
        file_content = Path(files[0]).read_bytes()
        assert b'foobar test!' in file_content
