from __future__ import annotations

import struct
from pathlib import Path

from unblob.handlers.filesystem.minifs import MiniFSExtractor

from helperFunctions.unblob import extract_file

NAME = 'tp-link-minifs'
MIME_PATTERNS = ['filesystem/tp-link-minifs']
VERSION = '0.1.0'
supported_versions = {3}
extractor = MiniFSExtractor()


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    path = Path(file_path)
    with path.open(mode='rb') as fp:
        fp.seek(16)
        version, file_count = struct.unpack('>II', fp.read(8))
        logs = f'version: {version}\nfile count: {file_count}\n'
        if version not in supported_versions:
            return {'output': logs + 'ERROR: unsupported version'}
    logs += extract_file(extractor, path, tmp_dir)
    return {'output': logs}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
