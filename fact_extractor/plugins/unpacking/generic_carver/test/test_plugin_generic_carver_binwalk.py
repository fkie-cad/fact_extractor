from test.unit.unpacker.test_unpacker import TestUnpackerBase
from helperFunctions.file_system import get_test_data_dir

# pylint: disable=protected-access


class TestGenericCarver(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('generic/carver', 'generic_carver')

    def test_extraction(self):
        in_file = '{}/generic_carver_test'.format(get_test_data_dir())
        files, meta_data = self.unpacker._extract_files_from_file_using_specific_unpacker(in_file, self.tmp_dir.name, self.unpacker.unpacker_plugins['generic/carver'])
        files = set(files)
        self.assertEqual(len(files), 1, 'file number incorrect')
        self.assertEqual(files, {'{}/64.zip'.format(self.tmp_dir.name)}, 'not all files found')
        self.assertIn('output', meta_data)
