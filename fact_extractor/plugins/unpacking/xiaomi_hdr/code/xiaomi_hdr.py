"""
This plugin uses unblob to unpack Xiaomi HDR1/2 images.
"""

from __future__ import annotations

from pathlib import Path

from unblob.handlers.archive.xiaomi.hdr import HDRExtractor

from helperFunctions.unblob import extract_file

NAME = 'Xiaomi HDR'
MIME_PATTERNS = ['firmware/xiaomi-hdr1', 'firmware/xiaomi-hdr2']
VERSION = '0.1.0'


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    path = Path(file_path)
    with path.open('rb') as fp:
        magic = fp.read(4)
    if magic in [b'HDR1', b'HDR2']:
        extractor = HDRExtractor(f'{magic.decode().lower()}_header_t')
    else:
        return {'output': ''}

    logs = extract_file(extractor, path, tmp_dir)
    return {'output': logs}


# ----> Do not edit below this line <----


def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
