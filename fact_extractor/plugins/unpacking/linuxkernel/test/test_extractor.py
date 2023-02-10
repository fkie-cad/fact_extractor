import os
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

INTERNAL_DIR = Path(__file__).parent.parent / 'internal'
sys.path.append(str(INTERNAL_DIR))
from extractor import Extractor  # noqa: E402 pylint: disable=import-error,wrong-import-position

SAMPLE_DATA = b'####-------\x1f\x8b\x08-------\x1f\x8b\x08$$$$BZh$$$$'


class TestExtractorCases:

    def test_find_offsets(self):
        with patch('builtins.open', mock_open(read_data=SAMPLE_DATA)) as mock_file:
            extract = Extractor('file_name', 'output_dir')
            mock_file.assert_called_with('file_name', 'rb')
            ret = extract._find_offsets()  # pylint: disable=protected-access
            assert ret == {'BZIP': [28], 'GZIP': [11, 21]}

    def test_extract_files(self):
        with patch('builtins.open', mock_open(read_data=SAMPLE_DATA)) as mock_file:
            output_dir = 'output_dir'
            extract = Extractor('file_name', output_dir)
            mock_file.assert_called_with('file_name', 'rb')

        with patch('builtins.open', mock_open(read_data='')) as mock_file:
            file_generator = extract.extracted_files()
            file_data = next(file_generator)
            assert file_data['file_path'] == os.path.join(output_dir, 'vmlinux_GZIP_11.gz')
            mock_file.assert_called_with('output_dir/vmlinux_GZIP_11.gz', 'wb')
            mock_file().write.assert_called_once_with(b'\x1f\x8b\x08-------\x1f\x8b\x08$$$$BZh$$$$')

        with patch('builtins.open', mock_open(read_data='')) as mock_file:
            file_data = next(file_generator)
            assert file_data['file_path'] == os.path.join(output_dir, 'vmlinux_GZIP_21.gz')
            mock_file.assert_called_with('output_dir/vmlinux_GZIP_21.gz', 'wb')
            mock_file().write.assert_called_once_with(b'\x1f\x8b\x08$$$$BZh$$$$')
