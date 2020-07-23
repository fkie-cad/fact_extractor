from subprocess import check_output

from plugins.unpacking.boschtool.code.boschtool import TOOL_PATH, unpack_function


def test_boschtool_works():
    output = check_output(f'{TOOL_PATH} --version', shell=True)
    assert output.strip() == b'1.0.0'


def test_boschtool():
    output = unpack_function()