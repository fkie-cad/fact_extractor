"""
Created on 21.08.2015

@author: weidenba
"""

from helperFunctions.hash import get_sha256


class TestHashGeneration:
    test_string = 'test string'
    test_string_SHA256 = 'd5579c46dfcc7f18207013e65b44e4cb4e2c2298f4ac457ba8f82743f31e930b'

    def test_get_sha256(self):
        assert get_sha256(self.test_string) == self.test_string_SHA256, 'not correct from string'
