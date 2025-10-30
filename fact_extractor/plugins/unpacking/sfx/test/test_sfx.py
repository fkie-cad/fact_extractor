from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestSfxUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        for mime in [
            'application/x-executable',
            'application/x-dosexec',
            'application/vnd.microsoft.portable-executable',
        ]:
            self.check_unpacker_selection(mime, 'SFX')

    def test_normal_elf_is_skipped(self):
        self._assert_not_unpacked(TEST_DATA_DIR / 'test_elf_normal')

    def test_normal_pe_with_rsrc_directory(self):
        self._assert_not_unpacked(TEST_DATA_DIR / 'test_rsrc')

    def test_no_section_headers(self):
        self._assert_not_unpacked(TEST_DATA_DIR / 'no_section_header.elf')

    def _assert_not_unpacked(self, test_file: Path):
        files, meta_data = self.unpacker.extract_files_from_file(test_file, self.tmp_dir.name)
        assert not files, 'no file should be extracted'
        assert 'will not be extracted' in meta_data['output']

    def test_self_extracting_archives(self):
        for file in ['test_elf_sfx', 'test_pe_sfx']:
            self.check_unpacking_of_standard_unpack_set(
                TEST_DATA_DIR / file, additional_prefix_folder='get_files_test', output=True
            )

    def test_piggy_extraction(self):
        test_file = TEST_DATA_DIR / 'piggy.elf'
        files, meta_data = self.unpacker.extract_files_from_file(str(test_file), self.tmp_dir.name)
        assert len(files) == 1
        assert Path(files[0]).read_bytes() == b'foobar\\ntest 1234\n'
