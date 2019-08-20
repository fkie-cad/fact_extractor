'''
This plug-in is intended to be used on flash-dumps and unknown file types.
It dumps ff-padded data-sections and encoded regions.
Additionally it trys to detect and extract lzma streams.
Supported encodings are:
 - intel hex
 - motorola s-record
 - tektronix
 - tektronix extended
'''
from common_helper_extraction import (
    cut_at_padding, dump_files, extract_lzma_streams,
    get_decompressed_lzma_streams, extract_encoded_streams, INTEL_HEX_REGEX, SRECORD_REGEX
)
from common_helper_files import get_binary_from_file

NAME = 'RAW'
MIME_PATTERNS = ['data/raw']
VERSION = '0.2'


def unpack_function(file_path, tmp_dir):
    raw_binary = get_binary_from_file(file_path)
    data_sections = _get_padding_seperated_sections(raw_binary)
    ihex_streams = extract_encoded_streams(raw_binary, INTEL_HEX_REGEX)
    srecord_streams = extract_encoded_streams(raw_binary, SRECORD_REGEX)
    lzma_streams = extract_lzma_streams(raw_binary)
    decompressed_lzma_streams = get_decompressed_lzma_streams(lzma_streams)

    dump_files(data_sections, tmp_dir)
    dump_files(ihex_streams, tmp_dir, suffix='.ihex')
    dump_files(srecord_streams, tmp_dir, suffix='.srec')
    dump_files(decompressed_lzma_streams, tmp_dir, suffix='_lzma_decompressed')
    return _get_meta_data(data_sections, ihex_streams, srecord_streams, lzma_streams)


def _get_meta_data(data_sections: list, ihex_streams: list, srecord_streams: list, lzma_streams: list) -> dict:
    meta_data = {
        'number_of_ff_padded_sections': len(data_sections),
        'number_of_ihex_streams': len(ihex_streams),
        'number_of_srecord_streams': len(srecord_streams),
        'number_of_lzma_streams': len(lzma_streams),
    }
    return meta_data


def _get_padding_seperated_sections(raw_binary: bytes) -> list:
    data_sections = cut_at_padding(raw_binary, padding_min_length=16, padding_pattern=b'\xff')
    if len(data_sections) == 1 and data_sections[0][0] == 0 and len(data_sections[0][1]) == len(raw_binary):  # data_section == raw_binary
        return []
    return data_sections


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
