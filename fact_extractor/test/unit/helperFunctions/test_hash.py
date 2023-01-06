'''
Created on 21.08.2015

@author: weidenba
'''
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from helperFunctions.hash import get_sha256, compute_sha256_of_file


class Test_hash_generation(unittest.TestCase):
    test_string = "test string"
    test_string_SHA256 = "d5579c46dfcc7f18207013e65b44e4cb4e2c2298f4ac457ba8f82743f31e930b"

    def test_get_sha256(self):
        self.assertEqual(get_sha256(self.test_string), self.test_string_SHA256, "not correct from string")

    def test_compute_sha256_of_file(self):
        data = b'-' * 2000

        with TemporaryDirectory(prefix='unit_test_') as tmp_dir:
            test_file = Path(tmp_dir) / 'test_file'
            with open(test_file, 'wb') as f:
                f.write(data)

            sha256 = compute_sha256_of_file(test_file)
            # test that the computed sha is the same with both methods
            self.assertEqual(get_sha256(data), sha256, "not correct from string")
