from __future__ import annotations

import logging
from contextlib import suppress
from typing import TYPE_CHECKING

from common_helper_files import safe_rglob
from common_helper_unpacking_classifier import (
    avg_entropy,
    get_file_size_without_padding,
)

from helperFunctions import magic
from helperFunctions.config import read_list_from_config

if TYPE_CHECKING:
    from configparser import ConfigParser
    from pathlib import Path

SMALL_SIZE_THRESHOLD = 255
VERY_SMALL_SIZE_THRESHOLD = 50
COMPRESS_ENTROPY_THRESHOLD_SMALL_FILE = 0.65


def add_unpack_statistics(extraction_dir: Path, meta_data: dict):
    unpacked_files, unpacked_directories = 0, 0
    for extracted_item in safe_rglob(extraction_dir):
        if extracted_item.is_file():
            unpacked_files += 1
        elif extracted_item.is_dir():
            unpacked_directories += 1

    meta_data['number_of_unpacked_files'] = unpacked_files
    meta_data['number_of_unpacked_directories'] = unpacked_directories


def get_unpack_status(file_path: Path, extracted_files: list[Path], meta_data: dict, config: ConfigParser):
    meta_data['summary'] = []
    meta_data['entropy'] = avg_entropy(file_path)

    if not extracted_files and meta_data.get('number_of_excluded_files', 0) == 0:
        compressed_types = read_list_from_config(config, 'ExpertSettings', 'compressed_file_types')
        mime = magic.from_file(file_path, mime=True)
        if mime in compressed_types or not _is_probably_compressed(
            file_path.stat().st_size, meta_data['entropy'], config
        ):
            meta_data['summary'] = ['unpacked']
        else:
            meta_data['summary'] = ['packed']
    else:
        _detect_unpack_loss(file_path, extracted_files, meta_data, config.getint('ExpertSettings', 'header_overhead'))


def _detect_unpack_loss(file_path: Path, extracted_files: list[Path], meta_data: dict, header_overhead: int):
    decoding_overhead = 1 - meta_data.get('encoding_overhead', 0)
    cleaned_size = get_file_size_without_padding(file_path, blocksize=1024) * decoding_overhead - header_overhead
    size_of_extracted_files = _total_size_of_extracted_files(extracted_files)
    meta_data['size_packed'] = cleaned_size
    meta_data['size_unpacked'] = size_of_extracted_files
    meta_data['summary'] = ['data lost'] if cleaned_size > size_of_extracted_files else ['no data lost']


def _total_size_of_extracted_files(extracted_files: list[Path]) -> int:
    total_size = 0
    for item in extracted_files:
        with suppress(OSError):
            total_size += item.stat().st_size
    return total_size


def _is_probably_compressed(file_size: int, entropy: float, config: ConfigParser) -> bool:
    if file_size <= VERY_SMALL_SIZE_THRESHOLD:
        logging.debug('could not determine compression: file too small')
        return False
    if file_size <= SMALL_SIZE_THRESHOLD:
        logging.debug('compression classification might be wrong: file is small')
        return entropy > COMPRESS_ENTROPY_THRESHOLD_SMALL_FILE
    return entropy > config.getfloat('ExpertSettings', 'unpack_threshold')
