from pathlib import Path

from test.unit.unpacker.test_unpacker import TestUnpackerBase

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestSqliteUnpacker(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('application/vnd.sqlite3', 'sqlite')

    def test_extraction_sqlite(self):
        in_file = TEST_DATA_DIR / 'example.db'
        assert in_file.is_file()
        files, meta = self.unpacker.extract_files_from_file(str(in_file), self.tmp_dir.name)
        assert meta['plugin_used'] == 'sqlite'
        assert len(files) == 4
        paths_by_file = {p.name: p for f in files if (p := Path(f))}
        assert set(paths_by_file) == {
            'test',
            'foo',
            'db_dump_DataWithoutPath_data.0',
            'db_dump_DataWithoutPath_data.1',
        }, 'not all files unpacked'
        assert paths_by_file['foo'].read_bytes() == b'foobar', 'file 1 not correctly unpacked'
        assert paths_by_file['test'].read_bytes() == b'test 1234', 'file 2 not correctly unpacked'

    def test_extraction_broken_db(self):
        in_file = TEST_DATA_DIR / 'broken.db'
        assert in_file.is_file()
        files, meta = self.unpacker.extract_files_from_file(str(in_file), self.tmp_dir.name)
        assert meta['plugin_used'] == 'sqlite'
        assert meta['output'] == 'Error: database disk image is malformed'
