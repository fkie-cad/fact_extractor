import json
import logging
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Dict, Tuple

from common_helper_files import human_readable_file_size
from common_helper_unpacking_classifier import avg_entropy, get_binary_size_without_padding, is_compressed

from helperFunctions.fileSystem import file_is_empty, get_file_type_from_path
from unpacker.unpackBase import UnpackBase


class Unpacker(UnpackBase):

    GENERIC_FS_FALLBACK_CANDIDATES = ['SquashFS']
    GENERIC_CARVER_FALLBACK_BLACKLIST = ['generic_carver', 'NOP', 'PaTool', 'SFX']
    VALID_COMPRESSED_FILE_TYPES = ['application/x-shockwave-flash', 'audio/mpeg', 'audio/ogg', 'image/png', 'image/jpeg', 'image/gif', 'video/mp4', 'video/ogg']
    HEADER_OVERHEAD = 256

    def __init__(self, config=None):
        super().__init__(config=config)
        self._shared_file_folder = Path(self.config.get('unpack', 'file_folder'))
        self._shared_report_folder = Path(self.config.get('unpack', 'report_folder'))

    def unpack(self, file_path):
        binary = Path(file_path).read_bytes()

        logging.debug('Extracting {}'.format(Path(file_path).name))

        tmp_dir = TemporaryDirectory(prefix='faf_unpack_')

        extracted_files, meta_data = self.extract_files_from_file(file_path, tmp_dir.name)
        extracted_files, meta_data = self._do_fallback_if_necessary(extracted_files, meta_data, tmp_dir.name, file_path)

        extracted_files = self.move_extracted_files(extracted_files)
        extracted_files = self.remove_duplicates(extracted_files)

        # These should be replaced
        self.add_unpack_statistics(tmp_dir.name, meta_data)
        self.get_unpack_status(file_path, binary, extracted_files, meta_data)

        self.cleanup(tmp_dir)

        Path(self._shared_report_folder, 'meta.json').write_text(json.dumps(meta_data))

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

    def get_unpack_status(self, file_path, binary, extracted_files, meta_data: Dict):
        meta_data["summary"] = []
        meta_data["entropy"] = avg_entropy(binary)

        if not extracted_files:
            meta_data["summary"] = (
                ["unpacked"]
                if (
                    get_file_type_from_path(file_path)["mime"]
                    in self.VALID_COMPRESSED_FILE_TYPES
                )
                or not is_compressed(
                    binary,
                    compress_entropy_threshold=self.config["ExpertSettings"].getfloat(
                        "unpack_threshold", 0.7
                    ),
                    classifier=avg_entropy,
                )
                else ["packed"]
            )
        else:
            self._detect_unpack_loss(binary, extracted_files, meta_data)

    def _detect_unpack_loss(self, binary: bytes, extracted_files: List[str], meta_data: Dict):
        decoding_overhead = 1 - meta_data.get('encoding_overhead', 0)
        cleaned_size = get_binary_size_without_padding(binary) * decoding_overhead - self.HEADER_OVERHEAD
        size_of_extracted_files = self._get_accumulated_size_of_extracted_files(extracted_files)
        meta_data['size packed -> unpacked'] = '{} -> {}'.format(human_readable_file_size(cleaned_size), human_readable_file_size(size_of_extracted_files))
        meta_data['summary'] = ['data lost'] if cleaned_size > size_of_extracted_files else ['no data lost']

    @staticmethod
    def _get_accumulated_size_of_extracted_files(extracted_files: List[str]) -> int:
        return sum(Path(item).stat().st_size for item in extracted_files)

    @staticmethod
    def add_unpack_statistics(extraction_dir: str, meta_data: Dict):
        unpacked_files, unpacked_directories = 0, 0
        for extracted_item in Path(extraction_dir).iterdir():
            if extracted_item.is_file():
                unpacked_files += 1
            elif extracted_item.is_dir():
                unpacked_directories += 1

        meta_data['number_of_unpacked_files'] = unpacked_files
        meta_data['number_of_unpacked_directories'] = unpacked_directories

    def move_extracted_files(self, file_paths: List[str]) -> List[Path]:
        extracted_files = list()
        for item in file_paths:
            if not file_is_empty(item):
                current_file = Path(self._shared_file_folder, Path(item).name)
                shutil.move(item, str(current_file))
                extracted_files.append(current_file)
        return extracted_files

    @staticmethod
    def remove_duplicates(extracted_files: List[Path]) -> List[Path]:
        # passing this until it has a sensible implementation
        return extracted_files
