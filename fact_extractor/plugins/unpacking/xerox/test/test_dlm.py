# pylint: disable=attribute-defined-outside-init

from pathlib import Path

from common_helper_files import get_binary_from_file

from fact_extractor.helperFunctions.hash import get_sha256
from fact_extractor.test.unit.unpacker.test_unpacker import TestUnpackerBase
from ..code.dlm import XeroxDLM

TEST_DATA_DIR = Path(Path(__file__).parent, 'data')


class TestXeroxDLM(TestUnpackerBase):
    def setup_method(self):
        super().setup_method()

        self.test_path = str(Path(TEST_DATA_DIR, 'DLM-First_1MB.DLM'))
        self.firmware_container = XeroxDLM(self.test_path)

    def test_unpacker_selection(self):
        self.check_unpacker_selection('firmware/xerox-dlm', 'XeroxDLM')

    def test_get_header_end_offset(self):
        expected_offset = 0x243
        assert expected_offset == self.firmware_container.get_header_end_offset()

    def test_get_signature(self):
        expected_signature = '90ec11f7b52468378362987a4ed9e56855070915887e6afe567e1c47875b29f9'
        assert expected_signature == self.firmware_container.get_signature()

    def test_get_dlm_version(self):
        expected = 'NO_DLM_VERSION_CHECK'
        assert expected == self.firmware_container.get_dlm_version()

    def test_get_dlm_name(self):
        expected = '080415_08142013'
        assert expected == self.firmware_container.get_dlm_name()

    def test_header_and_binary(self):
        files, meta_data = self.unpacker.extract_files_from_file(self.test_path, self.tmp_dir.name)
        files = set(files)
        assert len(files) == 1, 'file number incorrect'
        data_bin = get_binary_from_file(str(Path(self.tmp_dir.name, 'dlm_data.bin')))
        assert get_sha256(data_bin) == '701962b0d11f50d9129d5a1655ee054865e90cd1b547d40d590ea96f7dfb64eb'
        assert meta_data['dlm_version'] == 'NO_DLM_VERSION_CHECK', 'meta: dlm_version not correct'
        assert (
            meta_data['dlm_signature'] == '90ec11f7b52468378362987a4ed9e56855070915887e6afe567e1c47875b29f9'
        ), 'meta: dlm_signature not correct'
        assert meta_data['dlm_name'] == '080415_08142013', 'meta: dlm_name not correct'
        assert (
            meta_data['dlm_extraction_criteria'] == 'upgradeExtract.sh /tmp/080415_08142013.dnld'
        ), 'meta: dlm_criteria not correct'

    def test_str(self):
        assert str(self.firmware_container)[0:3] == 'DLM'
