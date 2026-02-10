from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import structlog
from structlog.testing import capture_logs

if TYPE_CHECKING:
    from unblob.models import Extractor

# configure unblob internal logger
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
)


def extract_file(extractor: Extractor, path: Path, tmp_dir: str) -> str:
    # unblob uses structlog for logging, but we can capture the logs with this convenient testing function
    with capture_logs() as log_list:
        extractor.extract(path, Path(tmp_dir))
        return _format_logs(log_list)


def _format_logs(logs: list[dict]) -> str:
    output = ''
    for entry in logs:
        output += '\n'.join(f'{key}: {value}' for key, value in entry.items() if key not in {'_verbosity', 'log_level'})
    return output
