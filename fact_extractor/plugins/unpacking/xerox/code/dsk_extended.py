import os
import sys

from common_helper_files import write_binary_to_file

THIS_FILE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(THIS_FILE, '..', 'internal'))

from dsk_container import ExtendedDskOne  # noqa: E402 pylint: disable=import-error,wrong-import-position

NAME = 'DSK-extended'
MIME_PATTERNS = ['firmware/dsk1.0-extended']
VERSION = '0.2'


def unpack_function(file_path, tmp_dir):
    container = ExtendedDskOne(file_path)

    write_binary_to_file(container.decoded_payload, os.path.join(tmp_dir, 'b64decoded_payload'))

    return container.get_meta_dict()


# ----> Do not edit below this line <----


def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
