import json
import logging
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Dict, Tuple

from helperFunctions.fileSystem import file_is_empty
from helperFunctions.statistics import get_unpack_status, add_unpack_statistics
from unpacker.unpackBase import UnpackBase


class Unpacker(UnpackBase):

    GENERIC_FS_FALLBACK_CANDIDATES = ['SquashFS']
    GENERIC_CARVER_FALLBACK_BLACKLIST = ['generic_carver', 'NOP', 'PaTool', 'SFX']

    def __init__(self, config=None):
        super().__init__(config=config)
        self._file_folder = Path(self.config.get('unpack', 'data_folder'), 'files')
        self._report_folder = Path(self.config.get('unpack', 'data_folder'), 'reports')

    def unpack(self, file_path):
        binary = Path(file_path).read_bytes()

        logging.debug('Extracting {}'.format(Path(file_path).name))

        tmp_dir = TemporaryDirectory(prefix='faf_unpack_')

        extracted_files, meta_data = self.extract_files_from_file(file_path, tmp_dir.name)
        extracted_files, meta_data = self._do_fallback_if_necessary(extracted_files, meta_data, tmp_dir.name, file_path)

        extracted_files = self.move_extracted_files(extracted_files, Path(tmp_dir.name))
        extracted_files = self.remove_duplicates(extracted_files)

        # These should be replaced
        add_unpack_statistics(self._file_folder, meta_data)
        get_unpack_status(file_path, binary, extracted_files, meta_data, self.config)

        self.cleanup(tmp_dir)

        Path(self._report_folder, 'meta.json').write_text(json.dumps(meta_data))

        return extracted_files

    def _do_fallback_if_necessary(self, extracted_files: List, meta_data: Dict, tmp_dir: str, file_path: str) -> Tuple[List, Dict]:
        if not extracted_files and meta_data['plugin_used'] in self.GENERIC_FS_FALLBACK_CANDIDATES:
            logging.warning('{} could not extract any files -> generic fs fallback'.format(meta_data['plugin_used']))
            extracted_files, meta_data = self.unpacking_fallback(file_path, tmp_dir, meta_data, 'generic/fs')
        if not extracted_files and meta_data['plugin_used'] not in self.GENERIC_CARVER_FALLBACK_BLACKLIST:
            logging.warning('{} could not extract any files -> generic carver fallback'.format(meta_data['plugin_used']))
            extracted_files, meta_data = self.unpacking_fallback(file_path, tmp_dir, meta_data, 'generic/carver')
        return extracted_files, meta_data

    @staticmethod
    def cleanup(tmp_dir: TemporaryDirectory):
        try:
            tmp_dir.cleanup()
        except OSError as error:
            logging.error('Could not CleanUp tmp_dir: {} - {}'.format(type(error), str(error)))

    def move_extracted_files(self, file_paths: List[str], extraction_dir: Path) -> List[Path]:
        extracted_files = list()
        for item in file_paths:
            if not file_is_empty(item):
                absolute_path = Path(item)
                relative_path = absolute_path.relative_to(extraction_dir)
                target_path = Path(self._file_folder, relative_path)
                os.makedirs(str(target_path.parent), exist_ok=True)
                shutil.move(absolute_path, target_path)
                extracted_files.append(target_path)
        return extracted_files

    @staticmethod
    def remove_duplicates(extracted_files: List[Path]) -> List[Path]:
        # passing this until it has a sensible implementation
        return extracted_files
