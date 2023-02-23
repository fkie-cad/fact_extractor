from pathlib import Path

from ..internal.uboot_container import uBootHeader

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestUbootImage:
    def test_header(self):
        ubh = uBootHeader()
        test_firmware = TEST_DATA_DIR / 'uboot.image_with_header'
        with test_firmware.open('r+b') as uboot_image:
            ubh.create_from_binary(uboot_image.read(64))
        assert ubh.image_data_size == 32753
        assert ubh.cpu_architecture == 5
        assert ubh.operating_system == 5
        assert ubh.image_type == 5
        assert ubh.image_name == 'u-boot image'
        assert ubh.image_data_crc == 0x385A8513
