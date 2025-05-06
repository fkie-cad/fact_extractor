from tempfile import NamedTemporaryFile, TemporaryDirectory

from plugins.unpacking.linuxkernel.internal.extractor import Extractor

SAMPLE_DATA = b'####-------\x1f\x8b\x08-------\x1f\x8b\x08$$$$BZh$$$$'
SAMPLE_DATA_BE32 = b'\xff\xff\xff\xff\xff\x08\x8b\x1f\x00boof21raet43ts'


class TestExtractorCases:
    def test_extract_files(self):
        with NamedTemporaryFile() as tmp_file, TemporaryDirectory() as tmp_dir:
            tmp_file.write(SAMPLE_DATA)
            tmp_file.seek(0)
            extract = Extractor(tmp_file.name, tmp_dir)
            assert extract.offsets == {'BZIP': [28], 'GZIP': [11, 21]}
            extracted_files = list(extract.get_extracted_files())
            assert len(extracted_files) == 3

            file, command = extracted_files[0]
            assert command == ['gunzip']
            assert file.name == 'vmlinux_GZIP_11.gz'
            assert file.read_bytes() == b'\x1f\x8b\x08-------\x1f\x8b\x08$$$$BZh$$$$'

            file, command = extracted_files[1]
            assert command == ['gunzip']
            assert file.name == 'vmlinux_GZIP_21.gz'
            assert file.read_bytes() == b'\x1f\x8b\x08$$$$BZh$$$$'

    def test_extract_be32(self):
        with NamedTemporaryFile() as tmp_file, TemporaryDirectory() as tmp_dir:
            tmp_file.write(SAMPLE_DATA_BE32)
            tmp_file.seek(0)
            extract = Extractor(tmp_file.name, tmp_dir)
            assert extract.offsets == {'GZIP_BE32': [5]}
            extracted_files = list(extract.get_extracted_files())
            assert len(extracted_files) == 1

            file, command = extracted_files[0]
            assert command == ['gunzip']
            assert file.name == 'vmlinux_GZIP_BE32_5.gz'
            assert file.read_bytes() == b'\x1f\x8b\x08foobar1234test'
