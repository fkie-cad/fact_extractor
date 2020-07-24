from pathlib import Path
from subprocess import check_output

from plugins.unpacking.boschtool.code.boschtool import TOOL_PATH
from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_FILE = Path(__file__).parent / 'data' / 'test.fw'


class TestBoschToolUnpacker(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/bosch', 'BoschFirmwareTool')

    def test_extraction(self):
        unpacked_files, meta_data = self.unpacker.extract_files_from_file(TEST_FILE, self.tmp_dir.name)
        print(f"\nunpacked_files: {unpacked_files}")
        for file in ['test_file_1.txt', 'test_file_2.txt']:
            assert file in meta_data['output'], 'test file not found'
            assert any(f.endswith(file) for f in unpacked_files)
        assert len(unpacked_files) == 2
        for file in unpacked_files:
            assert 'test file!' in Path(file).read_text()


def test_boschtool_works():
    output = check_output(f'{TOOL_PATH} --version', shell=True)
    assert output.strip() == b'1.0.0'
