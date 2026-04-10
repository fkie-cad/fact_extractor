# noqa: N999
from __future__ import annotations

import fnmatch
import logging
import re
from os import getgid, getuid
from pathlib import Path
from subprocess import PIPE, Popen
from time import time
from typing import Callable, Dict, List, Tuple

from common_helper_files import get_files_in_dir

from helperFunctions import magic
from helperFunctions.config import read_list_from_config
from helperFunctions.file_system import copy_file_offset_to_file
from helperFunctions.plugin import import_plugins

PADDING_END_REGEX = re.compile(rb'[^\x00\xff]')
TRAILING_DATA_MIN_SIZE = 2**10
CHUNK_SIZE = 2**20


class UnpackBase:
    """
    The unpacker module unpacks all files included in a file
    """

    def __init__(self, config=None):
        self.config = config
        self.exclude = read_list_from_config(config, 'unpack', 'exclude')
        self._setup_plugins()

    def _setup_plugins(self):
        self.unpacker_plugins = {}
        self.load_plugins()
        logging.debug(f'Plugins available: {self.source.list_plugins()}')
        self._set_whitelist()

    def load_plugins(self):
        self.source = import_plugins('unpacker.plugins', 'plugins/unpacking')
        for plugin_name in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin_name)
            plugin.setup(self)

    def _set_whitelist(self):
        self.blacklist = read_list_from_config(self.config, 'unpack', 'blacklist')
        logging.debug(f"""Ignore (Blacklist): {', '.join(self.blacklist)}""")
        for item in self.blacklist:
            self.register_plugin(item, self.unpacker_plugins['generic/nop'])

    def register_plugin(self, mime_type: str, unpacker_name_and_function: Tuple[Callable[[str, str], Dict], str, str]):
        self.unpacker_plugins[mime_type] = unpacker_name_and_function

    def get_unpacker(self, mime_type: str):
        if mime_type in list(self.unpacker_plugins.keys()):
            return self.unpacker_plugins[mime_type]
        return self.unpacker_plugins['generic/carver']

    def extract_files_from_file(self, file_path: str | Path, tmp_dir) -> Tuple[List, Dict]:
        current_unpacker = self.get_unpacker(magic.from_file(file_path, mime=True))
        return self._extract_files_from_file_using_specific_unpacker(str(file_path), tmp_dir, current_unpacker)

    def unpacking_fallback(self, file_path, tmp_dir, old_meta, fallback_plugin_mime) -> Tuple[List, Dict]:
        fallback_plugin = self.unpacker_plugins[fallback_plugin_mime]
        old_meta[f"""0_FALLBACK_{old_meta['plugin_used']}"""] = (
            f"""{old_meta['plugin_used']} (failed) -> {fallback_plugin_mime} (fallback)"""
        )
        if 'output' in old_meta:
            old_meta[f"""0_ERROR_{old_meta['plugin_used']}"""] = old_meta['output']
        return self._extract_files_from_file_using_specific_unpacker(
            file_path, tmp_dir, fallback_plugin, meta_data=old_meta
        )

    def should_ignore(self, file):
        path = str(file)
        return any(fnmatch.fnmatchcase(path, pattern) for pattern in self.exclude)

    def _extract_files_from_file_using_specific_unpacker(
        self, file_path: str, tmp_dir: str, selected_unpacker, meta_data: dict | None = None
    ) -> Tuple[List, Dict]:
        unpack_function, name, version = (
            selected_unpacker  # TODO Refactor register method to directly use four parameters instead of three
        )

        if meta_data is None:
            meta_data = {}
        meta_data['plugin_used'] = name
        meta_data['plugin_version'] = version

        path = Path(file_path)
        logging.info(f'Trying to unpack "{path.name}" with plugin {name}')

        try:
            additional_meta = unpack_function(file_path, tmp_dir)
        except Exception as error:
            logging.debug(f'Unpacking of {file_path} failed: {error}', exc_info=True)
            additional_meta = {'error': f'{type(error)}: {error!s}'}
        if isinstance(additional_meta, dict):
            meta_data.update(additional_meta)

        _check_for_trailing_data(meta_data, path, tmp_dir)

        self.change_owner_back_to_me(directory=tmp_dir)
        meta_data['analysis_date'] = time()

        out = get_files_in_dir(tmp_dir)

        if self.exclude:
            # Remove paths that should be ignored
            excluded_count = len(out)
            out = [f for f in out if not self.should_ignore(f)]
            excluded_count -= len(out)
        else:
            excluded_count = 0

        meta_data['number_of_excluded_files'] = excluded_count
        return out, meta_data

    def change_owner_back_to_me(self, directory: str, permissions: str = 'u+r'):
        with Popen(f'sudo chown -R {getuid()}:{getgid()} {directory}', shell=True, stdout=PIPE, stderr=PIPE) as pl:
            pl.communicate()
        self.grant_read_permission(directory, permissions)

    @staticmethod
    def grant_read_permission(directory: str, permissions: str):
        with Popen(f'chmod --recursive {permissions} {directory}', shell=True, stdout=PIPE, stderr=PIPE) as pl:
            pl.communicate()


def _check_for_trailing_data(meta: dict, path: Path, tmp_dir: str):
    # If we find trailing data, save it to a file in the output folder (otherwise the data is lost).
    if 'size' not in meta:
        return  # Only works with plugins that store the size of the unpacked file in meta['size']!
    file_end: int = meta['size']
    padding_end = _find_padding_end(path, file_end)
    file_size = path.stat().st_size
    if (file_size - padding_end) > TRAILING_DATA_MIN_SIZE:
        copy_file_offset_to_file(path, Path(tmp_dir) / 'trailing.bin', padding_end)
        meta['trailing_data'] = (
            f'found trailing data at {padding_end} ({file_size - padding_end} bytes). Saved as trailing.bin'
        )


def _find_padding_end(file: Path, fs_end_offset: int) -> int:
    with file.open('rb') as fp:
        fp.seek(fs_end_offset)
        relative_offset = fs_end_offset
        while chunk := fp.read(CHUNK_SIZE):
            if match := PADDING_END_REGEX.search(chunk):
                relative_offset += match.start()
                break
            relative_offset += len(chunk)
        return relative_offset
