from configparser import ConfigParser
from contextlib import suppress
from pathlib import Path
from typing import Dict, List

from common_helper_files import safe_rglob
from common_helper_unpacking_classifier import avg_entropy, get_binary_size_without_padding, is_compressed
from fact_helper_file import get_file_type_from_path

from helperFunctions.config import read_list_from_config


def add_unpack_statistics(extraction_dir: Path, meta_data: Dict):
    unpacked_files, unpacked_directories = 0, 0
    for extracted_item in safe_rglob(extraction_dir):
        if extracted_item.is_file():
            unpacked_files += 1
        elif extracted_item.is_dir():
            unpacked_directories += 1

    meta_data['number_of_unpacked_files'] = unpacked_files
    meta_data['number_of_unpacked_directories'] = unpacked_directories


def get_unpack_status(
    file_path: str, binary: bytes, extracted_files: List[Path], meta_data: Dict, config: ConfigParser
):
    meta_data['summary'] = []
    meta_data['entropy'] = avg_entropy(binary)

    if not extracted_files and meta_data.get('number_of_excluded_files', 0) == 0:
        if get_file_type_from_path(file_path)['mime'] in read_list_from_config(
            config, 'ExpertSettings', 'compressed_file_types'
        ) or not is_compressed(
            binary,
            compress_entropy_threshold=config.getfloat('ExpertSettings', 'unpack_threshold'),
            classifier=avg_entropy,
        ):
            meta_data['summary'] = ['unpacked']
        else:
            meta_data['summary'] = ['packed']
    else:
        _detect_unpack_loss(binary, extracted_files, meta_data, config.getint('ExpertSettings', 'header_overhead'))


def _detect_unpack_loss(binary: bytes, extracted_files: List[Path], meta_data: Dict, header_overhead: int):
    decoding_overhead = 1 - meta_data.get('encoding_overhead', 0)
    cleaned_size = get_binary_size_without_padding(binary) * decoding_overhead - header_overhead
    size_of_extracted_files = _total_size_of_extracted_files(extracted_files)
    meta_data['size_packed'] = cleaned_size
    meta_data['size_unpacked'] = size_of_extracted_files
    meta_data['summary'] = ['data lost'] if cleaned_size > size_of_extracted_files else ['no data lost']


def _total_size_of_extracted_files(extracted_files: List[Path]) -> int:
    total_size = 0
    for item in extracted_files:
        with suppress(OSError):
            total_size += item.stat().st_size
    return total_size
