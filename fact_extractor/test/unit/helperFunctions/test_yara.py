from helperFunctions.yara import get_yara_magic
from plugins.unpacking.dlink.test.test_dlink_dcs import TEST_DATA_DIR


def test_get_yara_magic():
    in_file = TEST_DATA_DIR / 'test_dcs.bin'
    assert get_yara_magic(in_file) == 'firmware/dlink-dcs-enc'
