"""
This plugin decrypts D-Link encrpted_img firmware images using unblob.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from unblob.handlers.archive.dlink.encrpted_img import EncrptedExtractor

NAME = 'D-Link encrpted_img'
MIME_PATTERNS = ['firmware/dlink-encrpted-img']
VERSION = '0.1.0'
extractor = EncrptedExtractor()


def unpack_function(file_path: str, tmp_dir: str) -> dict[str, Any]:
    input_path = Path(file_path)
    extractor.extract(input_path, Path(tmp_dir))
    return {'output': f'Decrypted image to {input_path.name}.decrypted'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
