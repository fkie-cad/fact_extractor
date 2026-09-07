"""
This plugin unpacks D-Link DEAFBEAD firmware containers using unblob.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from unblob.handlers.archive.dlink.deafbead import DeafBeadExtractor

NAME = 'D-Link DEAFBEAD'
MIME_PATTERNS = ['firmware/d-link-deafbead']
VERSION = '0.1.0'
extractor = DeafBeadExtractor()


def unpack_function(file_path: str, tmp_dir: str) -> dict[str, Any]:
    input_path = Path(file_path)
    extractor.extract(input_path, Path(tmp_dir))
    return {'output': 'Successfully unpacked DEAFBEAD container'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
