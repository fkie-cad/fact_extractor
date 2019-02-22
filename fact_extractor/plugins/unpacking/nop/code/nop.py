'''
This plugin does not unpack any files files.
'''

NAME = 'NOP'
MIME_PATTERNS = ['generic/nop', 'inode/symlink']
VERSION = '0.1'


def unpack_function(*_, **__):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    Optional: Return a dict with meta information
    """
    return {'info': 'unpacking skipped'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
