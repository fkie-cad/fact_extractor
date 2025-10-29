"""
This plugin unpacks Flattened Image Trees.
"""

from contextlib import suppress
from pathlib import Path

import libfdt as fdt
from common_helper_files import write_binary_to_file

NAME = 'FIT'
MIME_PATTERNS = ['linux/device-tree']
VERSION = '0.2.0'
TRAILING_DATA_MIN_SIZE = 100


def unpack_function(file_path, tmp_dir):
    file = Path(file_path)

    try:
        with file.open('rb') as f:
            fit_data = f.read()

        dtb = fdt.Fdt(fit_data)
        root_offset = dtb.path_offset('/')
        subnode_offset = dtb.first_subnode(root_offset)
        while True:
            try:
                component_offset = dtb.first_subnode(subnode_offset)
                while True:
                    try:
                        outfile = Path(tmp_dir) / dtb.get_name(component_offset)
                        with suppress(TypeError):
                            data = dtb.getprop(component_offset, 'data')
                            if data:
                                write_binary_to_file(bytes(data), outfile)
                        component_offset = dtb.next_subnode(component_offset)
                    except fdt.FdtException:
                        break
                subnode_offset = dtb.next_subnode(subnode_offset)
            except fdt.FdtException:
                break
    except OSError as io_error:
        return {'output': f'failed to read file: {io_error!s}'}
    message = 'successfully unpacked FIT image'

    dtb_size = dtb.size_dt_struct()
    trailing_data_size = len(fit_data) - dtb_size
    if trailing_data_size > TRAILING_DATA_MIN_SIZE:
        outfile = Path(tmp_dir) / 'trailing_data'
        outfile.write_bytes(fit_data[dtb_size:])
        message += f'\nfound trailing data and saved it to {outfile.name} ({trailing_data_size} bytes)'

    return {'output': message}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
