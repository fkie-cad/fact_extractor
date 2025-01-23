from __future__ import annotations

from pathlib import Path

from plugins.unpacking.sevenz.code.sevenz import unpack_function as sevenz

NAME = 'SFX'
MIME_PATTERNS = [
    'application/x-dosexec',
    'application/x-executable',
    'application/x-pie-executable',
]
VERSION = '0.2.0'

EXCLUDED_FILE_NAMES_1 = {'.bss', '.data', '.text'}
EXCLUDED_FILE_NAMES_2 = {str(i) for i in range(20)}


def _extraction_result_is_invalid(extraction_dir: Path) -> bool:
    extracted_files = [f.name for f in extraction_dir.iterdir()]
    if any(f in EXCLUDED_FILE_NAMES_1 for f in extracted_files):
        return True
    return all(f in EXCLUDED_FILE_NAMES_2 for f in extracted_files)


def unpack_function(file_path, tmp_dir):
    meta = sevenz(file_path, tmp_dir)

    extraction_dir = Path(tmp_dir)

    if _extraction_result_is_invalid(extraction_dir):
        clean_directory(extraction_dir)
        meta['output'] = (
            "Normal executable files will not be extracted.\n\nPlease report if it's a self extracting archive"
        )

    return meta


def clean_directory(directory: Path):
    for child in directory.iterdir():
        if not child.is_dir():
            child.unlink()
        else:
            clean_directory(child)


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
