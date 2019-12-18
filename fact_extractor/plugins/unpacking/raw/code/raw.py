'''
This plug-in is intended to be used on flash-dumps and unknown file types.
It dumps ff-padded data-sections and encoded regions.
Additionally it trys to detect and extract lzma streams.
Supported encodings are:
 - intel hex
 - motorola s-record
 - tektronix
 - tektronix extended
 - file systems
'''
from common_helper_extraction import EXTRACTOR_LIST, dump_files
from common_helper_files import get_binary_from_file

NAME = 'RAW'
MIME_PATTERNS = ['application/octet-stream', 'data/raw']
VERSION = '0.4'


def unpack_function(file_path, tmp_dir):
    raw_binary = get_binary_from_file(file_path)
    meta_data = dict()
    for extractor in EXTRACTOR_LIST:
        data_sections = extractor.extract_function(raw_binary, *extractor.optional_parameters)
        dump_files(data_sections, tmp_dir, suffix=extractor.file_suffix)
        meta_data[extractor.name] = len(data_sections)
    return meta_data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
