from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestTenvisPk2Unpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('firmware/pk2', 'tenvis_pk2')

    def test_extraction_pk2(self):
        in_file = TEST_DATA_DIR / 'test.pk2'
        assert in_file.is_file()
        files, meta = self.unpacker.extract_files_from_file(str(in_file), self.tmp_dir.name)
        assert meta['plugin_used'] == 'tenvis_pk2'
        assert len(files) == 2
        assert {Path(f).name for f in files} == {'bar', 'foo'}, 'not all files unpacked'
        output_file = Path(sorted(files)[1])
        assert output_file.read_bytes() == b'foobar\n', 'files not decrypted correctly'

        assert 'sections' in meta['output']
        assert len(meta['output']['sections']) == 3
        sections_by_offset = {s['offset']: s for s in meta['output']['sections']}
        assert set(sections_by_offset) == {28, 67, 111}
        assert sections_by_offset[28]['type'] == 'CMD'
        assert sections_by_offset[28]['command'] == 'echo "foobar"\n'

    def test_extraction_pk2_error(self):
        in_file = TEST_DATA_DIR / 'broken.pk2'
        assert in_file.is_file()
        files, meta = self.unpacker.extract_files_from_file(str(in_file), self.tmp_dir.name)
        assert meta['plugin_used'] == 'tenvis_pk2'
        assert len(files) == 0
        assert 'error' in meta['output']
        assert meta['output']['error'] == 'error while parsing section at offset 91'
