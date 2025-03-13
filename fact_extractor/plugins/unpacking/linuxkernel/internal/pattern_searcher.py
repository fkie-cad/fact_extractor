from __future__ import annotations


class PatternSearcher:
    def __init__(self, rawbytedata):
        self.algorithms = {
            'GZIP': {
                'magic': bytes.fromhex('1f 8b 08'),
                'suffix': 'gz',
                'command': ['gunzip'],
            },
            'GZIP_BE32': {
                'magic': bytes.fromhex('08 8b 1f'),  # this is the same magic as above but in reversed byte order
                'magic_offset': 1,  # since these are 32 bit blocks, there is one byte preceding this 3 byte magic
                'suffix': 'gz',
                'command': ['gunzip'],
            },
            'XZ': {
                'magic': b'\xfd7zXZ\x00',
                'suffix': 'xz',
                'command': ['unxz'],
            },
            'BZIP': {
                'magic': b'BZh',
                'suffix': 'bz',
                'command': ['bunzip2'],
            },
            'LZMA': {
                'magic': bytes.fromhex('5d 00 00 00'),
                'suffix': 'lzma',
                'command': ['unlzma'],
            },
            'LZOP': {
                'magic': bytes.fromhex('89 4c 5a'),
                'suffix': 'lzop',
                'command': ['lzop', '-d'],
            },
            'LZ4': {
                'magic': b'\x02!L\x18',
                'suffix': 'lz4',
                'command': ['lz4', '-d'],
            },
            'ZSTD': {
                'magic': b'(\xb5/\xfd',
                'suffix': 'zstd',
                'command': ['unzstd'],
            },
        }
        self.rawdata = rawbytedata

    def _find_offsets(self, magic: bytes) -> list[int]:
        index_list, index = [], -1
        while (index := self.rawdata.find(magic, index + 1)) != -1:
            index_list.append(index)
        return index_list

    def find_all_headers(self) -> dict[str, list[int]]:
        results = {}
        for algo_name, algo_data in self.algorithms.items():
            offsets = self._find_offsets(algo_data['magic'])
            if len(offsets):
                results[algo_name] = offsets

        return results

    def find_all_gzip_offsets(self) -> list[int]:
        return self._find_offsets(self.algorithms['GZIP']['magic'])
