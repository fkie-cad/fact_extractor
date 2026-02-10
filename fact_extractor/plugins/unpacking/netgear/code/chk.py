from __future__ import annotations

import struct
from pathlib import Path

from unblob.handlers.archive.netgear.chk import CHKExtractor

from helperFunctions.unblob import extract_file

NAME = 'netgear-chk'
MIME_PATTERNS = ['firmware/netgear-chk']
VERSION = '0.1.0'
extractor = CHKExtractor()


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    # Netgear CHK images are simple containers with a header (usually 58 bytes) that should contain a kernel and a
    # root filesystem. Their sizes should also be contained in the header at offsets 24 and 28 respectively.
    # A size of 0 indicates that the file is missing (which is the case for the 2nd file of most samples).
    # Since unblob comes with the capability to unpack these containers, we simply use its `CHKExtractor`.
    path = Path(file_path)
    with path.open(mode='rb') as fp:
        fp.seek(24)
        kernel_len, rootfs_len = struct.unpack('>II', fp.read(8))
        logs = f'kernel size: {kernel_len}\nrootfs size: {rootfs_len}\n'
    logs += extract_file(extractor, path, tmp_dir)
    return {'output': logs}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
