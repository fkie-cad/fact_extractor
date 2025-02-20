"""
This plugin uses unblob to unpack Xiaomi HDR1/2 images.
"""

from __future__ import annotations

import logging
from pathlib import Path

import structlog
from structlog.testing import capture_logs
from unblob.handlers.archive.xiaomi.hdr import HDRExtractor

NAME = 'Xiaomi HDR'
MIME_PATTERNS = ['firmware/xiaomi-hdr1', 'firmware/xiaomi-hdr2']
VERSION = '0.1.0'

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
)


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    path = Path(file_path)
    with path.open('rb') as fp:
        magic = fp.read(4)
    if magic in [b'HDR1', b'HDR2']:
        extractor = HDRExtractor(f'{magic.decode().lower()}_header_t')
    else:
        return {'output': ''}

    # unblob uses structlog for logging, but we can capture the logs with this convenient testing function
    with capture_logs() as log_list:
        extractor.extract(path, Path(tmp_dir))
        return {'output': _format_logs(log_list)}


def _format_logs(logs: list[dict]) -> str:
    output = ''
    for entry in logs:
        output += '\n'.join(f'{key}: {value}' for key, value in entry.items() if key not in {'_verbosity', 'log_level'})
    return output


# ----> Do not edit below this line <----


def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
