import unittest

from ..internal.pattern_searcher import PatternSearcher


class PatternSearcherTestCase(unittest.TestCase):

    def test_instance(self):
        data = b'####'
        ps = PatternSearcher(data)

        self.assertEqual(True, isinstance(ps, PatternSearcher))

    def test_search_gzip(self):
        data = b'####-------\037\213\010-------\037\213\010$$$$$$$$'
        ps = PatternSearcher(data)
        offsets = ps.find_all_gzip_offsets()
        self.assertEqual([11, 21], offsets)

    def test_search_all(self):
        data = b'####-------\037\213\010-------\037\213\010$$$$$$$$'
        data += b'\3757zXZ\000'
        data += b'BZh'
        data += b'\135\000\000\000'
        data += b'\211\114\132'
        data += b'\037\213\010'
        data += b'\002!L\030'
        data += b'(\265/\375'

        expected = {'BZIP': [38],
                    'GZIP': [11, 21, 48],
                    'LZ4': [51],
                    'LZMA': [41],
                    'LZOP': [45],
                    'XZ': [32],
                    'ZSTD': [55]}

        ps = PatternSearcher(data)
        offset_data = ps.find_all_headers()

        self.assertEqual(expected, offset_data)


if __name__ == '__main__':
    unittest.main()
