"""
This plugin unpacks all files via carving
"""

from __future__ import annotations

import logging
import re
import traceback
from collections.abc import Iterable
from itertools import chain
from pathlib import Path

from common_helper_unpacking_classifier import avg_entropy
from structlog.testing import capture_logs
from unblob.extractor import carve_unknown_chunk, carve_valid_chunk
from unblob.file_utils import File
from unblob.finder import logger, search_chunks
from unblob.handlers import BUILTIN_HANDLERS
from unblob.models import Chunk, PaddingChunk, TaskResult, UnknownChunk, ValidChunk
from unblob.processing import Task, calculate_unknown_chunks, remove_inner_chunks

from fact_extractor.plugins.unpacking.generic_carver.internal.handlers import CUSTOM_HANDLERS

NAME = 'generic_carver'
MIME_PATTERNS = ['generic/carver']
VERSION = '1.2.0'

MIN_FILE_ENTROPY = 0.01

# deactivate internal debug logging of unblob finder because it can slow down chunks search significantly
logger.debug = lambda *_, **__: None

# global loglevel gets set to critical when importing Unblob -> reset it
logging.getLogger().setLevel(logging.DEBUG)


HANDLERS = (*BUILTIN_HANDLERS, *CUSTOM_HANDLERS)


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    extraction_dir = Path(tmp_dir)
    chunks = []
    filter_report = ''
    path = Path(file_path)

    try:
        with File.from_path(path) as file, capture_logs() as _:
            for chunk in _find_chunks(path, file):
                if isinstance(chunk, PaddingChunk):
                    continue
                if isinstance(chunk, UnknownChunk):
                    if _has_low_entropy(file, chunk):
                        filter_report += (
                            f'removed chunk {chunk.start_offset}-{chunk.end_offset} (reason: low entropy)\n'
                        )
                        continue
                    carve_unknown_chunk(extraction_dir, file, chunk)
                else:
                    carve_valid_chunk(extraction_dir, file, chunk)
                chunks.append(chunk.as_report([] if isinstance(chunk, ValidChunk) else None).model_dump())

        report = _create_report(chunks) if chunks else 'No valid chunks found.'
        if filter_report:
            report += f'\nFiltered chunks:\n{filter_report}'
    except Exception as error:
        report = f'Error {error} during unblob extraction:\n{traceback.format_exc()}'
    _rename_extracted_files(Path(tmp_dir), path.stat().st_size)
    return {'output': report}


def _rename_extracted_files(tmp_dir: Path, filesize: int):
    """Default filenames are not sortable. This Function adds leading zeroes to the offsets to fix this."""
    pad_width = len(str(filesize))
    name_regex = re.compile(r'(\d+)-(\d+)\.(.+)')
    for file in tmp_dir.iterdir():
        if match := name_regex.match(file.name):
            start, end, extension = match.groups()
            filename = f'{int(start):0{pad_width}d}-{int(end):0{pad_width}d}.{extension}'
            file.rename(tmp_dir / filename)


def _find_chunks(file_path: Path, file: File) -> Iterable[Chunk]:
    task = Task(path=file_path, depth=0, blob_id='')
    known_chunks = remove_inner_chunks(search_chunks(file, file.size(), HANDLERS, TaskResult(task=task)))
    unknown_chunks = calculate_unknown_chunks(known_chunks, file.size())
    yield from chain(known_chunks, unknown_chunks)


def _create_report(chunk_list: list[dict]) -> str:
    report = ['Extracted chunks:']
    for chunk in sorted(chunk_list, key=lambda c: c['start_offset']):
        chunk_type = chunk.get('handler_name', 'unknown')
        report.append(
            f'start: {chunk["start_offset"]}, end: {chunk["end_offset"]}, size: {chunk["size"]}, type: {chunk_type}'
        )
    return '\n'.join(report)


def _has_low_entropy(file: File, chunk: UnknownChunk) -> bool:
    file.seek(chunk.start_offset)
    content = file.read(chunk.size)
    return avg_entropy(content) < MIN_FILE_ENTROPY


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
