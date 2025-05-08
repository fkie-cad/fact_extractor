"""
This plugin unpacks all files via carving
"""

from __future__ import annotations

import traceback
from itertools import chain
from pathlib import Path
from typing import Iterable

from common_helper_unpacking_classifier import avg_entropy
from structlog.testing import capture_logs
from unblob.extractor import carve_unknown_chunk, carve_valid_chunk
from unblob.file_utils import File
from unblob.finder import logger, search_chunks
from unblob.handlers import BUILTIN_HANDLERS
from unblob.models import Chunk, PaddingChunk, TaskResult, UnknownChunk
from unblob.processing import Task, calculate_unknown_chunks, remove_inner_chunks

from plugins.unpacking.generic_carver.internal.handlers import CUSTOM_HANDLERS

NAME = 'generic_carver'
MIME_PATTERNS = ['generic/carver']
VERSION = '1.1.0'

MIN_FILE_ENTROPY = 0.01

# deactivate internal debug logging of unblob finder because it can slow down chunks search significantly
logger.debug = lambda *_, **__: None


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
                chunks.append(chunk.as_report(None).asdict())

        report = _create_report(chunks) if chunks else 'No valid chunks found.'
        if filter_report:
            report += f'\nFiltered chunks:\n{filter_report}'
    except Exception as error:
        report = f'Error {error} during unblob extraction:\n{traceback.format_exc()}'
    return {'output': report}


def _find_chunks(file_path: Path, file: File) -> Iterable[Chunk]:
    task = Task(path=file_path, depth=0, blob_id='')
    known_chunks = remove_inner_chunks(search_chunks(file, file.size(), HANDLERS, TaskResult(task)))
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
