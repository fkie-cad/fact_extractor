class PatternSearcher:
    def __init__(self, rawbytedata):
        self.algorithms = {
            'GZIP': {
                'magic': b'\037\213\010',
                'suffix': 'gz',
                'command': ['gunzip']
            },
            'XZ': {
                'magic': b'\3757zXZ\000',
                'suffix': 'xz',
                'command': ['unxz']
            },
            'BZIP': {
                'magic': b'BZh',
                'suffix': 'bz',
                'command': ['bunzip2']
            },
            'LZMA': {
                'magic': b'\135\000\000\000',
                'suffix': 'lmza',
                'command': ['unlzma']
            },
            'LZOP': {
                'magic': b'\211\114\132',
                'suffix': 'lzop',
                'command': ['lzop', '-d']
            },
            'LZ4': {
                'magic': b'\002!L\030',
                'suffix': 'lz4',
                'command': ['lz4', '-d']
            },
            'ZSTD': {
                'magic': b'(\265/\375',
                'suffix': 'zstd',
                'command': ['unzstd']
            },
        }
        self.rawdata = rawbytedata

    def _find_offsets(self, magic):
        idxs = []
        idx = self.rawdata.find(magic)
        while -1 != idx:
            idxs.append(idx)
            idx = self.rawdata.find(magic, idx + 1)
        return idxs

    def find_all_headers(self):
        results = {}
        for algo in self.algorithms:
            offsets = self._find_offsets(self.algorithms[algo]['magic'])
            if len(offsets):
                results[algo] = offsets

        return results

    def find_all_gzip_offsets(self):
        return self._find_offsets(self.algorithms['GZIP']['magic'])
