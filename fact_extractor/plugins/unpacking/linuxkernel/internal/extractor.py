from __future__ import annotations

from pathlib import Path
from typing import Iterable

from plugins.unpacking.linuxkernel.internal.pattern_searcher import PatternSearcher


class Extractor:
    def __init__(self, file_path: str, output_dir: str):
        self.file_path = Path(file_path)
        self.output_dir = Path(output_dir)
        with self.file_path.open('rb') as f:
            self.raw_data = f.read()
        self.ps = PatternSearcher(self.raw_data)
        self.offsets = self.ps.find_all_headers()

    @staticmethod
    def _get_reversed_chunks(data: bytes, offset: int, chunk_size: int) -> Iterable[bytes]:
        # converts endianness of data and returns it as chunks
        for i in range(offset, len(data), chunk_size):
            yield data[i : i + chunk_size][::-1]

    def get_extracted_files(self) -> Iterable[tuple[Path, str]]:
        for algo in self.offsets:
            for offset in self.offsets[algo]:
                filename = f'vmlinux_{algo}_{offset}.{self.ps.algorithms[algo]["suffix"]}'
                file_path = Path(self.output_dir) / filename
                if algo.endswith('BE32'):
                    data = b''.join(self._get_reversed_chunks(self.raw_data, offset, 32 // 8))
                    magic_offset = self.ps.algorithms[algo].get('magic_offset', 0)
                    if magic_offset > 0:
                        data = data[magic_offset:]
                else:
                    data = self.raw_data[offset:]
                file_path.write_bytes(data)
                yield file_path, self.ps.algorithms[algo]['command']
