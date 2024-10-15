'''
This plugin unpacks Flattened Image Trees.
'''

from pathlib import Path
from common_helper_files import write_binary_to_file

NAME = 'FIT'
MIME_PATTERNS = ['linux/device-tree']
VERSION = '0.1'

def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir must be used to store the extracted files.
    Optional: Return a dict with meta information
    '''

    try:
        with open(file_path, 'rb') as f:
            fit_data = f.read()
        
        dtb = fdt.Fdt(fit_data)
        root_offset = dtb.path_offset('/')
        subnode_offset = dtb.first_subnode(root_offset)
        while True:
            try:
                component_offset = dtb.first_subnode(subnode_offset)
                while True:
                    try:
                        property_offset = dtb.first_property_offset(component_offset)
                        outfile = Path(tmp_dir) / dtb.get_name(component_offset)
                        write_binary_to_file(bytes(dtb.getprop(component_offset, 'data')), outfile)
                        component_offset = dtb.next_subnode(component_offset)
                    except fdt.FdtException:
                        break
                subnode_offset = dtb.next_subnode(subnode_offset)
            except fdt.FdtException:
                break
    except IOError as io_error:
        return {'output': 'failed to read file: {}'.format(str(io_error))}

    return {
        'output': 'successfully unpacked FIT image'
    }

# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
