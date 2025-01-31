"""
This plugin decodes / unpacks Intel HEX files (.hex)
"""

from pathlib import Path

from intelhex import HexRecordError, IntelHex, IntelHexError

NAME = 'IntelHEX'
MIME_PATTERNS = ['firmware/intel-hex']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    target_file = Path(tmp_dir, Path(file_path).name)

    try:
        hex_object = IntelHex(file_path)
        hex_object.tofile(str(target_file.absolute()), format='bin')
    except HexRecordError:
        return {'output': 'Invalid hex file'}
    except IntelHexError as intel_hex_error:
        return {'output': f'Unknown error in decoding: {intel_hex_error!s}'}

    return {'output': 'Successfully decoded hex file'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
