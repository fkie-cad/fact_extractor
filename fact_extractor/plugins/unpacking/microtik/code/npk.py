'''
Based on [npkPy](https://github.com/botlabsDev/npkpy) of @botlabsDev
Used to extract Mikrotik firmware files
'''
from pathlib import Path

from npkpy.common import getFullPktInfo, extractContainer
from npkpy.npk.npk import Npk
from npkpy.npk.npkConstants import CNT_HANDLER

NAME = 'Micotic NPK files'
MIME_PATTERNS = ['firmware/microtic-npk']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    try:
        npk_file = Npk(Path(file_path))
    except RuntimeError:
        return {'error': 'Invalid file. No npk magic found.'}

    meta = {'output': getFullPktInfo(npk_file)}

    export_folder = Path(tmp_dir) / '{}'.format(npk_file.file.stem)
    export_folder.mkdir(parents=True, exist_ok=True)

    extractContainer(npk_file, export_folder, CNT_HANDLER.keys())

    return meta


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
