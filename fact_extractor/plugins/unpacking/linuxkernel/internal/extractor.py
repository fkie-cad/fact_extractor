import os

from pattern_searcher import PatternSearcher


class Extractor:
    def __init__(self, file_path, output_dir):
        self.file_path = file_path
        self.output_dir = output_dir
        with open(file_path, 'rb') as f:
            self.raw_data = f.read()
        self.ps = PatternSearcher(self.raw_data)
        self.offsets = self.ps.find_all_headers()

    def _find_offsets(self):
        return self.offsets

    def extracted_files(self):
        for algo in self.offsets:
            for offset in self.offsets[algo]:
                fn = 'vmlinux_{}_{}.{}'.format(algo, offset, self.ps.algorithms[algo]['suffix'])
                file_path = os.path.join(self.output_dir, fn)
                with open(file_path, 'wb') as f:
                    f.write(self.raw_data[offset:])
                yield {'file_path': file_path, 'command': self.ps.algorithms[algo]['command']}
