"""
This plugin uses unblob to unpack UNIX fast filesystem images.
"""

from __future__ import annotations

import logging
from pathlib import Path
from subprocess import run

import structlog
from unblob.handlers.filesystem.ufs import SolarisHandler, UFS1Handler, UFS2Handler

from helperFunctions.unblob import extract_file

NAME = 'UNIX FFS'
MIME_PATTERNS = ['filesystem/ffs']
VERSION = '0.1.0'

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
)
HANDLERS = (UFS1Handler, UFS2Handler, SolarisHandler)
REGEX_TO_EXTRACTOR = {pattern.as_regex(): handler.EXTRACTOR for handler in HANDLERS for pattern in handler.PATTERNS}


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    path = Path(file_path)
    for regex, extractor in REGEX_TO_EXTRACTOR.items():
        proc = run(
            ['grep', '-Pboa', regex, file_path],
            check=False,
            capture_output=True,
        )
        if proc.returncode != 0:
            continue

        logs = extract_file(extractor, path, tmp_dir)
        return {'output': logs}
    raise ValueError('Magic not found')


# ----> Do not edit below this line <----


def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
