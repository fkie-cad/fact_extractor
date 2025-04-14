# noqa: N999
from __future__ import annotations

import fnmatch
import logging
from os import getgid, getuid
from pathlib import Path
from time import time
from typing import Any, Iterable

from common_helper_files import get_files_in_dir

from helperFunctions import magic
from helperFunctions.config import read_list_from_config
from helperFunctions.file_system import change_owner_of_output_files
from helperFunctions.plugin import find_plugin_classes, import_plugins
from plugins.base_class import UnpackingPlugin


class UnpackBase:
    """
    The unpacker module unpacks all files included in a file
    """

    def __init__(self, config=None):
        self.config = config
        self.exclude = read_list_from_config(config, 'unpack', 'exclude')
        self._setup_plugins()

    def _setup_plugins(self):
        self.unpacking_plugins: dict[str, UnpackingPlugin] = {}
        self.plugin_by_mime: dict[str, str] = {}
        self.load_plugins()
        logging.info(f'Plugins available: {", ".join(self.unpacking_plugins)}')
        self._set_blacklist()

    def load_plugins(self):
        for module in import_plugins():
            for plugin in self._get_unpackers_from_module(module):
                self.register_plugin(plugin)

    @staticmethod
    def _get_unpackers_from_module(module) -> Iterable[UnpackingPlugin]:
        classes = list(find_plugin_classes(module))
        if not classes:
            # fallback for old plugins without the base class
            classes = [UnpackingPlugin.from_old_module(module)]
        for plugin_class in classes:
            try:
                plugin = plugin_class()
                plugin.validate()
                yield plugin
            except Exception as error:
                logging.exception(f'Could not instantiate plugin from {module}: {error}')

    def _set_blacklist(self):
        self.blacklist = read_list_from_config(self.config, 'unpack', 'blacklist')
        logging.debug(f"""Ignore (Blacklist): {', '.join(self.blacklist)}""")
        for mime in self.blacklist:
            self.plugin_by_mime[mime] = 'NOP'

    def register_plugin(self, plugin: UnpackingPlugin):
        self.unpacking_plugins[plugin.NAME] = plugin
        for mime in plugin.MIME_PATTERNS:
            self.plugin_by_mime[mime] = plugin.NAME

    def get_unpacker(self, mime_type: str) -> UnpackingPlugin:
        plugin = self.plugin_by_mime.get(mime_type)
        return self.unpacking_plugins.get(plugin if plugin else 'generic_carver')

    def extract_files_from_file(self, file_path: str | Path, tmp_dir) -> tuple[list, dict]:
        current_unpacker = self.get_unpacker(magic.from_file(file_path, mime=True))
        return self._extract_files_from_file_using_specific_unpacker(str(file_path), tmp_dir, current_unpacker)

    def unpacking_fallback(self, file_path, tmp_dir, old_meta, fallback_plugin_mime) -> tuple[list, dict]:
        fallback_plugin = self.get_unpacker(fallback_plugin_mime)
        old_meta[f"""0_FALLBACK_{old_meta['plugin_used']}"""] = (
            f"""{old_meta['plugin_used']} (failed) -> {fallback_plugin_mime} (fallback)"""
        )
        if 'output' in old_meta:
            old_meta[f"""0_ERROR_{old_meta['plugin_used']}"""] = old_meta['output']
        return self._extract_files_from_file_using_specific_unpacker(file_path, tmp_dir, fallback_plugin, old_meta)

    def should_ignore(self, file):
        path = str(file)
        return any(fnmatch.fnmatchcase(path, pattern) for pattern in self.exclude)

    def _extract_files_from_file_using_specific_unpacker(
        self, file_path: str, tmp_dir: str, selected_unpacker: UnpackingPlugin, old_meta: dict | None = None
    ) -> tuple[list[str], dict[str, Any]]:
        meta_data = old_meta or {}
        meta_data |= {'plugin_used': selected_unpacker.NAME, 'plugin_version': selected_unpacker.VERSION}

        logging.debug(f'Trying to unpack {Path(file_path).name} with {selected_unpacker.NAME} plugin...')
        try:
            additional_meta = selected_unpacker.unpack_file(file_path, tmp_dir)
        except Exception as error:
            logging.debug(f'Unpacking of {file_path} failed: {error}', exc_info=True)
            additional_meta = {'error': f'{type(error)}: {error!s}'}
        if isinstance(additional_meta, dict):
            meta_data.update(additional_meta)

        meta_data['analysis_date'] = time()
        change_owner_of_output_files(Path(tmp_dir), f'{getuid()}:{getgid()}')
        unpacked_files = get_files_in_dir(tmp_dir)
        meta_data['number_of_excluded_files'] = self._remove_excluded_files(unpacked_files)

        return unpacked_files, meta_data

    def _remove_excluded_files(self, file_list: list[str]) -> int:
        count = 0
        if self.exclude:
            for path in list(file_list):
                if self.should_ignore(path):
                    count += 1
                    file_list.remove(path)
        return count
