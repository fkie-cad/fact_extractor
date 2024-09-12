import os

from common_helper_files import get_binary_from_file

from fact_extractor.test.unit.unpacker.test_unpacker import TestUnpackerBase
from ..code.postscript import _get_raw_payloads, _convert_payloads

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

TEST_FILE = os.path.join(TEST_DATA_DIR, 'xerox.ps')


class TestUnpackerPluginPostscript(TestUnpackerBase):

    def test_unpacker_selection_adobe_ps(self):
        mimes = ['text/postscript']
        for item in mimes:
            self.check_unpacker_selection(item, 'Postscript')

    def test_extraction(self):
        files, meta_data = self.unpacker.extract_files_from_file(TEST_FILE, self.tmp_dir.name)
        assert meta_data['plugin_used'] == 'Postscript', 'wrong plugin selected'
        assert meta_data['Title'] == 'Firmware Update', 'meta data not set correctly'
        assert meta_data['ReleaseVersions'] == 'vx=10.80,ps=4.19.0,net=44.38,eng=26.P.1.4.19.0'
        assert meta_data['encoding_overhead'] == 0.25, 'encoding overhead not correct'
        assert len(meta_data.keys()) == 11, 'number of found meta data not correct'
        assert len(files) == 3, 'Number of extracted files not correct'

    def test_convert_payloads(self):
        raw_payloads = [b'<~FCfN8~>', b'<~FCfN8?YjFoAR\nAneART?~>']
        result = _convert_payloads(raw_payloads)
        assert result[0] == b'test', 'simple payload not correct'
        assert result[1] == b'test_line_break', 'line breaked payload not correct'

    def test_get_raw_payloads(self):
        raw_content = get_binary_from_file(TEST_FILE)
        payloads = _get_raw_payloads(raw_content)
        assert len(payloads) == 3, "number of payloads not correct"
        assert payloads[0] == b'<~<+oue+DGm>FD,5.Anc:,F<FCgH#.D-A0C~>', "simple payload not correct"
        assert payloads[1] == b'<~<+oue+DGm>@3BW&@rH6q+Dl72BHV,0DJ*O$+E1b7Ci<`m+EV:*F<GX<Dfol,+Cf>-FCAm$+\nEM+;ATD3q+Dbb0ATJu&DIal2D]it9/hSa~>', "multiline payload not correct"
        assert payloads[2] == b'<~@;^"*BOu3kAoD^,@<;~>', "other header format"
