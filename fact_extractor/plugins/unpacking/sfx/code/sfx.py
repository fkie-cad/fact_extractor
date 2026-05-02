from __future__ import annotations

import logging
from pathlib import Path

import lief

from plugins.unpacking.sevenz.code.sevenz import unpack_function as sevenz

NAME = 'SFX'
MIME_PATTERNS = [
    'application/vnd.microsoft.portable-executable',
    'application/x-dosexec',
    'application/x-executable',
    'application/x-pie-executable',
]
VERSION = '0.3.0'

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
        if output := _try_to_extract_piggy_data(file_path, tmp_dir):
            return {'output': output}
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


def _try_to_extract_piggy_data(file_path: str, tmp_dir: str) -> str | None:
    """
    Some build tools put the compressed kernel image in a .piggydata section in the ELF file
    """
    try:
        if (elf := lief.ELF.parse(file_path)) is None:
            return None
        sections = {s.name: s for s in elf.sections}
        if '.piggydata' not in sections:
            return None
        piggy = sections['.piggydata']
        output_file = Path(tmp_dir) / '.piggydata'
        with Path(file_path).open('rb') as fp_in, output_file.open('wb') as fp_out:
            fp_in.seek(piggy.offset)
            fp_out.write(fp_in.read(piggy.size))
        return f'Saved .piggydata section from offset {piggy.offset} with size {piggy.size} to .piggydata'
    except Exception as err:
        logging.exception(f'Error when trying to extract .piggydata section from ELF: {err}')
    return None


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
