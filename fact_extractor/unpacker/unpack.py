import json
import logging
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Dict, Tuple

from helperFunctions.dataConversion import ReportEncoder
from helperFunctions.file_system import file_is_empty
from helperFunctions.statistics import get_unpack_status, add_unpack_statistics
from unpacker.unpackBase import UnpackBase


class Unpacker(UnpackBase):

    FS_FALLBACK_CANDIDATES = ['SquashFS']
    CARVER_FALLBACK_BLACKLIST = ['generic_carver', 'NOP', 'PaTool', 'SFX']

    def __init__(self, config=None):
        super().__init__(config=config)
        self._file_folder = Path(self.config.get('unpack', 'data_folder'), 'files')
        self._report_folder = Path(self.config.get('unpack', 'data_folder'), 'reports')

    def unpack(self, file_path):
        if self._should_ignore(file_path):
            meta_data = {
                'plugin_used': None,
                'number_of_unpacked_files': 0,
                'number_of_unpacked_directories': 0,
                'number_of_excluded_files': 1,
                'info': 'File was ignored because it matched the exclude list {}'.format(
                    self.exclude
                )
            }
            extracted_files = []
        else:
            logging.debug('Extracting {}'.format(Path(file_path).name))

            tmp_dir = TemporaryDirectory(prefix='fact_unpack_')

            extracted_files, meta_data = self.extract_files_from_file(file_path, tmp_dir.name)
            extracted_files, meta_data = self._do_fallback_if_necessary(extracted_files, meta_data, tmp_dir.name, file_path)

            extracted_files = self.move_extracted_files(extracted_files, Path(tmp_dir.name))

            add_unpack_statistics(self._file_folder, meta_data)
            get_unpack_status(file_path, binary, extracted_files, meta_data, self.config)

            compute_stats = self.config.getboolean('ExpertSettings', 'statistics', fallback=True)
            if compute_stats:
                binary = Path(file_path).read_bytes()
                add_unpack_statistics(self._file_folder, meta_data)
                get_unpack_status(file_path, binary, extracted_files, meta_data, self.config)

            self.cleanup(tmp_dir)

        Path(self._report_folder, 'meta.json').write_text(json.dumps(meta_data, cls=ReportEncoder, indent=4))

        return extracted_files

    def _do_fallback_if_necessary(self, extracted_files: List, meta_data: Dict, tmp_dir: str, file_path: str) -> Tuple[List, Dict]:
        if meta_data.get('number_of_excluded_files', 0) > 0:
            # If files have been excluded, extracted_files might be empty, but
            # that doesn't mean there was an error during unpacking
            return extracted_files, meta_data

        if not extracted_files and meta_data['plugin_used'] in self.FS_FALLBACK_CANDIDATES:
            logging.warning('{} could not extract any file from {} -> generic fs fallback'.format(meta_data['plugin_used'], file_path))
            extracted_files, meta_data = self.unpacking_fallback(file_path, tmp_dir, meta_data, 'generic/fs')
        if not extracted_files and meta_data['plugin_used'] not in self.CARVER_FALLBACK_BLACKLIST:
            logging.warning('{} could not extract any file from {} -> generic carver fallback'.format(meta_data['plugin_used'], file_path))
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
                shutil.move(str(absolute_path), str(target_path))
                extracted_files.append(target_path)
        return extracted_files


def unpack(file_path, config):
    extracted_objects = Unpacker(config).unpack(file_path)
    logging.info('{} files extracted'.format(len(extracted_objects)))
    logging.debug('Extracted files:\n{}'.format('\n'.join((str(path) for path in extracted_objects))))
