"""
This plugin unpacks Flattened Image Trees.
"""

from __future__ import annotations

import bz2
import gzip
import lzma
from pathlib import Path

import libfdt as fdt

NAME = 'FIT'
MIME_PATTERNS = ['linux/device-tree']
VERSION = '0.2.0'

DECOMPRESSORS = {
    'gzip': gzip.decompress,
    'lzma': lzma.decompress,
    'bzip2': bz2.decompress,
    # FixMe: add lzo and lz4 decompressors
}

try:
    from compression import zstd

    DECOMPRESSORS['zstd'] = zstd.decompress
except ImportError:
    pass  # zstd decompression (zstd was added in Python 3.14)


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    file = Path(file_path)

    dtb = fdt.Fdt(file.read_bytes())
    root_offset = dtb.path_offset('/')
    output = extract_nodes(dtb, root_offset, tmp_dir, Path())
    output.append('successfully unpacked FIT image')
    return {'output': '\n'.join(output)}


def extract_nodes(dtb: fdt.Fdt, offset: int, tmp_dir: str, path: Path) -> list[str]:
    try:
        child_offset = dtb.first_subnode(offset)
    except fdt.FdtException:
        return []  # no child nodes in this node

    output = []
    while True:
        try:
            name = dtb.get_name(child_offset)
            current_path = path / name

            try:
                data = _read_from_dtb_at(dtb, child_offset)
                output_path = (Path(tmp_dir) / current_path).with_suffix('.bin')
                output_path.parent.mkdir(exist_ok=True)
                output_path.write_bytes(data)
                output.append(f'unpacked data from node {current_path} ({len(data)} bytes)')
            except (TypeError, fdt.FdtException):
                pass  # no "data" entry

            # recurse through child nodes
            output.extend(extract_nodes(dtb, child_offset, tmp_dir, current_path))

            child_offset = dtb.next_subnode(child_offset)
        except fdt.FdtException:
            break
    return output


def _read_from_dtb_at(dtb: fdt.Fdt, offset: int) -> bytes:
    data = bytes(dtb.getprop(offset, 'data'))
    try:
        compression = dtb.getprop(offset, 'compression').as_str()
        decompressor = DECOMPRESSORS[compression]
        return decompressor(data)
    except (fdt.FdtException, KeyError):
        return data


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
