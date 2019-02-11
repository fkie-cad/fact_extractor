from configparser import ConfigParser
from pathlib import Path

import pytest

from helperFunctions.fileSystem import get_test_data_dir
from helperFunctions.statistics import get_unpack_status, _detect_unpack_loss


@pytest.fixture(scope='function')
def common_tmpdir(tmpdir):
    return tmpdir


@pytest.fixture(scope='function')
def config_fixture(common_tmpdir):
    config = ConfigParser()
    config.add_section('unpack')
    config.set('unpack', 'data_folder', str(common_tmpdir))
    config.add_section('ExpertSettings')
    config.set('ExpertSettings', 'unpack_threshold', '0.8')
    return config


def test_unpack_status_packed_file(config_fixture):
    test_packed_file_path = Path(get_test_data_dir(), 'container/test.7z')

    result = dict()
    get_unpack_status(test_packed_file_path, test_packed_file_path.read_bytes(), list(), result, config_fixture)

    assert result['entropy'] > 0.7, 'entropy not valid'
    assert result['summary'] == ['packed'], '7z file should be packed'

    result = dict()
    config_fixture.set('ExpertSettings', 'compressed_file_types', 'application/x-7z-compressed, ')
    get_unpack_status(test_packed_file_path, test_packed_file_path.read_bytes(), list(), result, config_fixture)
    assert result['summary'] == ['unpacked'], 'Unpacking Whitelist does not work'


def test_unpack_status_unpacked_file(config_fixture):
    result = dict()
    get_unpack_status(Path('/dev/null'), b'aaaaa', list(), result, config_fixture)

    assert result['entropy'] < 0.7, 'entropy not valid'
    assert result['summary'] == ['unpacked']


def test_detect_unpack_loss_data_lost(config_fixture, common_tmpdir):
    included_file = Path(common_tmpdir, 'inner')
    included_file.write_bytes(256 * b'ABCDEFGH')
    result = {'summary': []}

    _detect_unpack_loss(512 * b'ABCDEFGH', [included_file, ], result, 256)
    assert 'data lost' in result['summary']
    assert result['size_packed'] == 512 * len(b'ABCDEFGH') - 256
    assert result['size_unpacked'] == 256 * len(b'ABCDEFGH')


def test_detect_unpack_loss_no_data_lost(config_fixture, common_tmpdir):
    included_file = Path(common_tmpdir, 'inner')
    included_file.write_bytes(512 * b'ABCDEFGH')
    result = {'summary': []}

    _detect_unpack_loss(512 * b'ABCDEFGH', [included_file, ], result, 256)
    assert 'no data lost' in result['summary']
