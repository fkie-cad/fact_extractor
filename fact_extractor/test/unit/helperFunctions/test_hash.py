'''
Created on 21.08.2015

@author: weidenba
'''
import unittest

from helperFunctions.hash import get_sha256


class Test_hash_generation(unittest.TestCase):
    test_string = "test string"
    test_string_SHA256 = "d5579c46dfcc7f18207013e65b44e4cb4e2c2298f4ac457ba8f82743f31e930b"

    def test_get_sha256(self):
        self.assertEqual(get_sha256(self.test_string), self.test_string_SHA256, "not correct from string")
