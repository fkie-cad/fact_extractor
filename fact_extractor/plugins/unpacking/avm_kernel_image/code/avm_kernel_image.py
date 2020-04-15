from common_helper_extraction import extract_lzma_streams, dump_files, get_decompressed_lzma_streams
from common_helper_extraction.fs import extract_sqfs
from common_helper_files import get_binary_from_file


NAME = 'avm_kernel_image'
MIME_PATTERNS = ['linux/avm-kernel-image-v1', 'linux/avm-kernel-image-v2']
VERSION = '0.1'

AVM_LZMA_HEADER = b'\x5d\x00\x00\x80\x00\x00\x00'
FIXED_LZMA_HEADER = b'\x5d\x00\x00\x00\x02' + 8 * b'\xff'


def unpack_function(file_path, tmp_dir):
    raw_binary = get_binary_from_file(file_path)

    decompressed_lzma_streams = _get_decompress_lzma_streams(raw_binary)
    dump_files(decompressed_lzma_streams, tmp_dir)

    file_systems = extract_sqfs(raw_binary)
    dump_files(file_systems, tmp_dir, suffix='.sqfs')

    return _get_meta_data(decompressed_lzma_streams, file_systems)


def _get_meta_data(lzma_streams: list, file_systems: list) -> dict:
    meta_data = {
        'number_of_lzma_streams': len(lzma_streams),
        'number_of_file_systems': len(file_systems)
    }
    return meta_data


def _get_decompress_lzma_streams(raw_binary: bytes) -> list:
    lzma_streams = extract_lzma_streams(raw_binary, header=AVM_LZMA_HEADER)
    _fix_streams(lzma_streams)
    return get_decompressed_lzma_streams(lzma_streams)


def _fix_streams(lzma_streams: list) -> None:
    for stream in lzma_streams:
        stream[1] = _fix_lzma_header(stream[1])


def _fix_lzma_header(lzma_stream: bytes) -> bytes:
    return FIXED_LZMA_HEADER + lzma_stream[8:]


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
