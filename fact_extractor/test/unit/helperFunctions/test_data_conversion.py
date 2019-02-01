import pytest

from helperFunctions.dataConversion import make_bytes, make_unicode_string, make_list_from_dict, \
    get_value_of_first_key, remove_uneccessary_spaces


@pytest.mark.parametrize('input_data', [
    ('test string'),
    (b'test string'),
    ([116, 101, 115, 116, 32, 115, 116, 114, 105, 110, 103])
])
def test_make_bytes(input_data):
    result = make_bytes(input_data)
    assert isinstance(result, bytes)
    assert result == b'test string'


@pytest.mark.parametrize('input_data, expected', [
    ('test string', 'test string'),
    (b'test string', 'test string'),
    (b'\xc3\xbc test string', 'ü test string'),
    (b'\xf5 test string', '� test string'),
    (['test string'], '[\'test string\']')
])
def test_make_unicode_string(input_data, expected):
    result = make_unicode_string(input_data)
    assert isinstance(result, str)
    assert result == expected


def test_make_list_from_dict():
    test_dict = {'a': 'abc', 'b': 'bcd'}
    result_list = make_list_from_dict(test_dict)
    assert isinstance(result_list, list), 'type is not list'
    result_list.sort()
    assert result_list == ['abc', 'bcd'], 'resulting list not correct'


@pytest.mark.parametrize('input_data, expected', [
    ({'b': 'b', 'c': 'c', 'a': 'a'}, 'a'),
    ({}, None)
])
def test_get_value_of_first_key(input_data, expected):
    assert get_value_of_first_key(input_data) == expected


@pytest.mark.parametrize('input_data, expected', [
    (' test', 'test'),
    ('blah   blah ', 'blah blah')
])
def test_remove_uneccessary_spaces(input_data, expected):
    assert remove_uneccessary_spaces(input_data) == expected
