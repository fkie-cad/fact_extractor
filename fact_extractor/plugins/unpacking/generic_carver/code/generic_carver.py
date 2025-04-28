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
from unblob.finder import search_chunks
from unblob.handlers import BUILTIN_HANDLERS
from unblob.handlers.compression.zlib import ZlibHandler
from unblob.models import Chunk, HexString, PaddingChunk, TaskResult, UnknownChunk
from unblob.processing import Task, calculate_unknown_chunks, remove_inner_chunks

NAME = 'generic_carver'
MIME_PATTERNS = ['generic/carver']
VERSION = '1.0.1'

MIN_FILE_ENTROPY = 0.01


class ZlibCarvingHandler(ZlibHandler):
    NAME = 'zlib_carver'

    PATTERNS = [  # noqa: RUF012
        HexString('78 01'),  # low compression
        HexString('78 9c'),  # default compression
        HexString('78 da'),  # best compression
        HexString('78 5e'),  # compressed
    ]


HANDLERS = (*BUILTIN_HANDLERS, ZlibCarvingHandler)


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    extraction_dir = Path(tmp_dir)
    chunks = []
    filter_report = ''
    path = Path(file_path)

    try:
        with File.from_path(path) as file, capture_logs() as log_list:
            # unblob uses structlog for logging, but we can capture the logs with this convenient testing function
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

        report = _format_logs(log_list)
        if filter_report:
            report += f'\nFiltered chunks:\n{filter_report}'
        if not chunks:
            report += '\nNo valid chunks found.'
    except Exception as error:
        report = f'Error {error} during unblob extraction:\n{traceback.format_exc()}'
    return {'output': report}


def _format_logs(logs: list[dict]) -> str:
    output = ''
    for entry in logs:
        output += '\n'.join(f'{key}: {value}' for key, value in entry.items() if key not in {'_verbosity', 'log_level'})
    return output


def _find_chunks(file_path: Path, file: File) -> Iterable[Chunk]:
    task = Task(path=file_path, depth=0, blob_id='')
    known_chunks = remove_inner_chunks(search_chunks(file, file.size(), HANDLERS, TaskResult(task)))
    unknown_chunks = calculate_unknown_chunks(known_chunks, file.size())
    yield from chain(known_chunks, unknown_chunks)


def _has_low_entropy(file: File, chunk: UnknownChunk) -> bool:
    file.seek(chunk.start_offset)
    content = file.read(chunk.size)
    return avg_entropy(content) < MIN_FILE_ENTROPY


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
