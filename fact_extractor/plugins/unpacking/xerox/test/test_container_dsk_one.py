import gc
import os

from helperFunctions.hash import get_sha256
from plugins.unpacking.xerox.internal.dsk_container import ExtendedDskOne

from ..internal.dsk_container import DskOne

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestContainerDSKone:
    def test_init_dsk(self):
        test_file = os.path.join(TEST_DATA_DIR, 'test.dsk1')
        test_obj = DskOne(test_file)
        assert test_obj.raw[1:4] == b'DSK', 'Raw Data not set correct'
        assert test_obj.header[1] == b'DSK1.0', 'header parsing not correct'
        assert test_obj.payload_size == 860293, 'payload length not correct'
        assert (
            get_sha256(test_obj.decoded_payload) == '057e936e6c1d45d617fe52decd532776c95c06a1b5e4a8f752d4227a645e5edc'
        ), 'payload checksum not correct'

    def test_error_handling_dsk(self):
        test_file = os.path.join(TEST_DATA_DIR, 'invalid_file')
        test_obj = DskOne(test_file)
        assert len(test_obj.errors) > 0, 'errors should be present'

        test_obj.header = b'inv'
        test_obj.HEADERSIZE = 0
        test_obj.payload_size = 1
        test_obj.check_validity()
        meta = test_obj.get_meta_dict()
        test_obj.log_errors_and_warnings()

        assert 'unpack errors' in meta, 'errors missing in dict'
        assert 'unpack warnings' in meta, 'warnings missing in dict'

        test_obj.payload_size = 1000
        test_obj.check_validity()
        assert test_obj.errors[-1] in 'payload length longer than file: 1000 -> 7'

    def test_error_handling_dsk_ext(self):
        test_file = os.path.join(TEST_DATA_DIR, 'invalid_file')
        test_obj = ExtendedDskOne(test_file)
        assert 'Extended DSK error' in test_obj.meta, 'errors missing'

    def teardown_method(self):
        gc.collect()
