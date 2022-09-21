import logging
from os import getgid, getuid
from subprocess import PIPE, Popen
from time import time
import fnmatch
from typing import Callable, Dict, List, Tuple

from common_helper_files import get_files_in_dir
from fact_helper_file import get_file_type_from_path
from helperFunctions.config import read_list_from_config
from helperFunctions.plugin import import_plugins


class UnpackBase(object):
    '''
    The unpacker module unpacks all files included in a file
    '''

    def __init__(self, config=None, extract_everything: bool = False):
        self.config = config
        self.exclude = read_list_from_config(config, 'unpack', 'exclude')
        self._setup_plugins()
        self.extract_everything = extract_everything

    def _setup_plugins(self):
        self.unpacker_plugins = {}
        self.load_plugins()
        logging.info(f'Plug-ins available: {self.source.list_plugins()}')
        self._set_whitelist()

    def load_plugins(self):
        self.source = import_plugins('unpacker.plugins', 'plugins/unpacking')
        for plugin_name in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin_name)
            plugin.setup(self)

    def _set_whitelist(self):
        self.blacklist = read_list_from_config(self.config, 'unpack', 'blacklist')
        logging.debug(f'''Ignore (Blacklist): {', '.join(self.blacklist)}''')
        for item in self.blacklist:
            self.register_plugin(item, self.unpacker_plugins['generic/nop'])

    def register_plugin(self, mime_type: str, unpacker_name_and_function: Tuple[Callable[[str, str], Dict], str, str]):
        self.unpacker_plugins[mime_type] = unpacker_name_and_function

    def get_unpacker(self, mime_type: str):
        if mime_type in list(self.unpacker_plugins.keys()):
            return self.unpacker_plugins[mime_type]
        else:
            return self.unpacker_plugins['generic/carver']

    def extract_files_from_file(self, file_path: str, tmp_dir) -> Tuple[List, Dict]:
        current_unpacker = self.get_unpacker(get_file_type_from_path(file_path)['mime'])
        return self._extract_files_from_file_using_specific_unpacker(file_path, tmp_dir, current_unpacker)

    def unpacking_fallback(self, file_path, tmp_dir, old_meta, fallback_plugin_mime) -> Tuple[List, Dict]:
        fallback_plugin = self.unpacker_plugins[fallback_plugin_mime]
        old_meta[f'''0_FALLBACK_{old_meta['plugin_used']}'''] = f'''{old_meta['plugin_used']} (failed) -> {fallback_plugin_mime} (fallback)'''
        if 'output' in old_meta.keys():
            old_meta[f'''0_ERROR_{old_meta['plugin_used']}'''] = old_meta['output']
        return self._extract_files_from_file_using_specific_unpacker(file_path, tmp_dir, fallback_plugin, meta_data=old_meta)

    def _should_ignore(self, file):
        path = str(file)
        for pattern in self.exclude:
            if fnmatch.fnmatchcase(path, pattern):
                return True
        return False

    def _extract_files_from_file_using_specific_unpacker(self, file_path: str, tmp_dir: str, selected_unpacker, meta_data: dict = None) -> Tuple[List, Dict]:
        unpack_function, name, version = selected_unpacker  # TODO Refactor register method to directly use four parameters instead of three

        if meta_data is None:
            meta_data = {}
        meta_data['plugin_used'] = name
        meta_data['plugin_version'] = version

        logging.debug(f'Try to unpack {file_path} with {name} plugin...')

        try:
            additional_meta = unpack_function(file_path, tmp_dir)
        except Exception as error:
            logging.debug(f'Unpacking of {file_path} failed: {error}', exc_info=True)
            additional_meta = {'error': f'{type(error)}: {str(error)}'}
        if isinstance(additional_meta, dict):
            meta_data.update(additional_meta)

        self.change_owner_back_to_me(directory=tmp_dir)
        meta_data['analysis_date'] = time()

        out = get_files_in_dir(tmp_dir)

        if self.exclude:
            # Remove paths that should be ignored
            excluded_count = len(out)
            out = [f for f in out if not self._should_ignore(f)]
            excluded_count -= len(out)
        else:
            excluded_count = 0

        meta_data['number_of_excluded_files'] = excluded_count
        return out, meta_data

    def change_owner_back_to_me(self, directory: str = None, permissions: str = 'u+r'):
        with Popen(f'sudo chown -R {getuid()}:{getgid()} {directory}', shell=True, stdout=PIPE, stderr=PIPE) as pl:
            pl.communicate()
        self.grant_read_permission(directory, permissions)

    @staticmethod
    def grant_read_permission(directory: str, permissions: str):
        with Popen(f'chmod --recursive {permissions} {directory}', shell=True, stdout=PIPE, stderr=PIPE) as pl:
            pl.communicate()
