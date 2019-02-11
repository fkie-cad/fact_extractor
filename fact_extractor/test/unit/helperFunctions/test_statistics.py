


def test_unpack_status_packed_file(self):
    test_packed_file_path = Path(get_test_data_dir(), 'container/test.7z')

    self.unpacker.get_unpack_status(test_fo_packed, [])
    result = test_fo_packed.processed_analysis['unpacker']
    self.assertGreater(result['entropy'], 0.7, 'entropy not valid')
    self.assertEqual(result['summary'], ['packed'], '7z file should be packed')
    self.unpacker.VALID_COMPRESSED_FILE_TYPES = ['application/x-7z-compressed']
    self.unpacker.get_unpack_status(test_fo_packed, [])
    self.assertEqual(test_fo_packed.processed_analysis['unpacker']['summary'], ['unpacked'],
                     'Unpacking Whitelist does not work')


def test_unpack_status_unpacked_file(self):
    test_fo_unpacked = FileObject(binary='aaaaa')
    test_fo_unpacked.file_path = '/dev/null'
    test_fo_unpacked.processed_analysis['unpacker'] = {}
    self.unpacker.get_unpack_status(test_fo_unpacked, [])
    result = test_fo_unpacked.processed_analysis['unpacker']
    self.assertLess(result['entropy'], 0.7, 'entropy not valid')
    self.assertEqual(result['summary'], ['unpacked'])


def test_detect_unpack_loss_data_lost(self):
    container = FileObject(binary=512 * 'ABCDEFGH')
    container.processed_analysis['unpacker'] = {'summary': []}
    included_file = FileObject(binary=256 * 'ABCDEFGH')
    self.unpacker._detect_unpack_loss(container, [included_file])
    self.assertIn('data lost', container.processed_analysis['unpacker']['summary'])
    self.assertEqual(container.processed_analysis['unpacker']['size packed -> unpacked'], '3.75 KiB -> 2.00 KiB')


def test_detect_unpack_loss_no_data_lost(self):
    container = FileObject(binary=512 * 'ABCDEFGH')
    container.processed_analysis['unpacker'] = {'summary': []}
    included_file = FileObject(binary=512 * 'ABCDEFGH')
    self.unpacker._detect_unpack_loss(container, [included_file])
    self.assertIn('no data lost', container.processed_analysis['unpacker']['summary'])
    self.assertNotIn('data loss', container.processed_analysis['unpacker'])
