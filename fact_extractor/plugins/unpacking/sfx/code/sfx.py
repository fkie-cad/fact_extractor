from pathlib import Path

import fact_extractor.plugins.unpacking.sevenz
import fact_extractor
# This is not an actual import due to wired pluginbase shenanigans.
# The 'sevenz' module is actually the 'code.sevenz' module.
from fact_extractor.plugins.unpacking.sevenz import unpack_function as sevenz

NAME = 'SFX'
MIME_PATTERNS = ['application/x-executable', 'application/x-dosexec']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    meta = sevenz(file_path, tmp_dir)

    extraction_dir = Path(tmp_dir)

    for child_path in extraction_dir.iterdir():
        if child_path.name in ['.text', '.data']:
            clean_directory(extraction_dir)
            meta['output'] = 'Normal executable files will not be extracted.' \
                             '\n\nPlease report if it\'s a self extracting archive'
            break

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
