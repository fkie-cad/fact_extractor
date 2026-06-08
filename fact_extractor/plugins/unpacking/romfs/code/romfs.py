from pathlib import Path

from unblob.handlers.filesystem.romfs import RomfsExtractor

from helperFunctions.unblob import extract_file

NAME = 'romfs'
MIME_PATTERNS = {'filesystem/romfs'}
VERSION = '0.1.0'

extractor = RomfsExtractor()


def unpack_function(file_path: str, tmp_dir: str):
    logs = extract_file(extractor, Path(file_path), tmp_dir)
    return {'output': logs}


# ----> Do not edit below this line <----


def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
