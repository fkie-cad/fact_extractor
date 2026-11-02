import json
from configparser import ConfigParser
from pathlib import Path

import pytest

from helperFunctions.file_system import get_test_data_dir
from helperFunctions.statistics import _add_chi_square_statistics, _detect_unpack_loss, get_unpack_status


@pytest.fixture
def common_tmpdir(tmpdir):
    return tmpdir


@pytest.fixture
def config_fixture(common_tmpdir):
    config = ConfigParser()
    config.add_section('unpack')
    config.set('unpack', 'data_folder', str(common_tmpdir))
    config.add_section('ExpertSettings')
    config.set('ExpertSettings', 'unpack_threshold', '0.8')
    return config


def test_unpack_status_packed_file(config_fixture):
    test_packed_file_path = Path(get_test_data_dir(), 'container/test.7z')

    result = {}
    get_unpack_status(test_packed_file_path, test_packed_file_path.read_bytes(), [], result, config_fixture)

    assert result['entropy'] > 0.7, 'entropy not valid'
    assert result['summary'] == ['packed'], '7z file should be packed'
    assert {'chi_square', 'chi_square_p_value'} <= result.keys()

    result = {}
    config_fixture.set('ExpertSettings', 'compressed_file_types', 'application/x-7z-compressed, ')
    get_unpack_status(test_packed_file_path, test_packed_file_path.read_bytes(), [], result, config_fixture)
    assert result['summary'] == ['unpacked'], 'Unpacking Whitelist does not work'


def test_unpack_status_unpacked_file(config_fixture):
    result = {}
    get_unpack_status(Path('/dev/null'), b'aaaaa', [], result, config_fixture)

    assert result['entropy'] < 0.7, 'entropy not valid'
    assert result['summary'] == ['unpacked']
    assert {'chi_square', 'chi_square_p_value'} <= result.keys()


@pytest.mark.parametrize(
    ('binary', 'expected_chi_square', 'expected_p_value'),
    [
        (bytes(range(256)) * 8, 0.0, 1.0),  # perfectly uniform
        (b'a' * 2048, 255 * 2048, 0.0),  # constant
        (bytes(range(256)) * 5, 0.0, 1.0),  # exactly the minimum size for the p-value (1280 bytes)
    ],
)
def test_add_chi_square_statistics(binary, expected_chi_square, expected_p_value):
    result = {}
    _add_chi_square_statistics(binary, result)

    assert result['chi_square'] == pytest.approx(expected_chi_square)
    assert result['chi_square_p_value'] == pytest.approx(expected_p_value)


@pytest.mark.parametrize('binary', [b'', b'aaaaa', (bytes(range(256)) * 5)[:-1]])
def test_add_chi_square_statistics_too_small(binary):
    result = {}
    _add_chi_square_statistics(binary, result)

    assert result['chi_square_p_value'] is None
    assert json.loads(json.dumps(result, allow_nan=False)) == result, 'must be valid JSON (NaN is not)'


def test_detect_unpack_loss_data_lost(config_fixture, common_tmpdir):
    included_file = Path(str(common_tmpdir), 'inner')
    included_file.write_bytes(256 * b'ABCDEFGH')
    result = {'summary': []}

    _detect_unpack_loss(
        512 * b'ABCDEFGH',
        [
            included_file,
        ],
        result,
        256,
    )
    assert 'data lost' in result['summary']
    assert result['size_packed'] == 512 * len(b'ABCDEFGH') - 256
    assert result['size_unpacked'] == 256 * len(b'ABCDEFGH')


def test_detect_unpack_loss_no_data_lost(config_fixture, common_tmpdir):
    included_file = Path(str(common_tmpdir), 'inner')
    included_file.write_bytes(512 * b'ABCDEFGH')
    result = {'summary': []}

    _detect_unpack_loss(
        512 * b'ABCDEFGH',
        [
            included_file,
        ],
        result,
        256,
    )
    assert 'no data lost' in result['summary']
