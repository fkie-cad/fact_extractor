'''
This plugin decodes / unpacks Adobe ASCII85 streams
'''
import base64
from pathlib import Path

NAME = 'Adobe ASCII85'
MIME_PATTERNS = ['firmware/adobe85']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    target_file = Path(tmp_dir, Path(file_path).name)
    try:
        enc = Path(file_path).read_bytes().decode('unicode_escape')

        try:
            decoded = base64.a85decode(enc, adobe=True)
            Path(target_file).write_bytes(decoded)
        except ValueError as v_err:
            return {'output': 'Unknown error in adobe85 stream decoding: {}'.format(str(v_err))}

    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}

    return {'output': 'Successfully decoded adobe85 stream'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
