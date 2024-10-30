from pathlib import Path

import magic

from helperFunctions.file_system import get_fact_bin_dir, get_test_data_dir


def test_magic():
    firmware_magic_path = Path(get_fact_bin_dir()) / 'firmware'
    assert firmware_magic_path.is_file()

    assert (
        magic.from_file(f'{get_test_data_dir()}/ros_header', mime=True) == 'firmware/ros'
    ), 'firmware-magic-database is not loaded'
    assert magic.from_file(f'{get_test_data_dir()}/container/test.zip', mime=True) == 'application/zip'
