'''
Based on [npkPy](https://github.com/botlabsDev/npkpy) of @botlabsDev
Used to extract Mikrotik firmware files
'''
from pathlib import Path

from npkpy.common import get_full_pkt_info, extract_container, NPKMagicBytesError
from npkpy.npk.npk import Npk
from npkpy.npk.npk_constants import CNT_HANDLER

NAME = 'MikroTik NPK files'
MIME_PATTERNS = ['firmware/mikrotik-npk']
VERSION = '0.2'


def unpack_function(file_path, tmp_dir):
    try:
        npk_file = Npk(Path(file_path))
    except NPKMagicBytesError:
        return {'error': 'Invalid file. No npk magic found.'}

    meta = {'output': get_full_pkt_info(npk_file)}

    export_folder = Path(tmp_dir) / f"{npk_file.file.stem}"
    export_folder.mkdir(parents=True, exist_ok=True)

    extract_container(npk_file, export_folder, CNT_HANDLER.keys())

    return meta


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
