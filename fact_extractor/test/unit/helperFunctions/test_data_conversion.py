import json

import pytest

from helperFunctions.dataConversion import ReportEncoder, make_bytes, make_unicode_string, remove_uneccessary_spaces


@pytest.mark.parametrize(
    'input_data', [('test string'), (b'test string'), ([116, 101, 115, 116, 32, 115, 116, 114, 105, 110, 103])]
)
def test_make_bytes(input_data):
    result = make_bytes(input_data)
    assert isinstance(result, bytes)
    assert result == b'test string'


@pytest.mark.parametrize(
    'input_data, expected',
    [
        ('test string', 'test string'),
        (b'test string', 'test string'),
        (b'\xc3\xbc test string', 'ü test string'),
        (b'\xf5 test string', '� test string'),
        (['test string'], "['test string']"),
    ],
)
def test_make_unicode_string(input_data, expected):
    result = make_unicode_string(input_data)
    assert isinstance(result, str)
    assert result == expected


def test_make_list_from_dict():
    test_dict = {'a': 'abc', 'b': 'bcd'}
    result_list = list(test_dict.values())
    assert isinstance(result_list, list), 'type is not list'
    result_list.sort()
    assert result_list == ['abc', 'bcd'], 'resulting list not correct'


@pytest.mark.parametrize('input_data, expected', [(' test', 'test'), ('blah   blah ', 'blah blah')])
def test_remove_uneccessary_spaces(input_data, expected):
    assert remove_uneccessary_spaces(input_data) == expected


@pytest.mark.parametrize(
    'source, result',
    [
        (b'abc', '"abc"'),
        (b'\x00\xff', '"00ff"'),
        (('ab', 'cd'), '["ab", "cd"]'),
        ({1, 3, 7}, '"[1, 3, 7]"'),
        ((i for i in range(3)), '"[0, 1, 2]"'),
    ],
)
def test_report_encoder_success(source, result):
    assert result == json.dumps(source, cls=ReportEncoder)


def test_report_encoder_failure():
    with pytest.raises(TypeError):
        json.dumps(lambda x: 5, cls=ReportEncoder)
