import logging
from pathlib import Path

from common_helper_files import get_dirs_in_dir
from pluginbase import PluginBase

from helperFunctions.file_system import get_src_dir


def import_plugins(plugin_mount, plugin_base_dir):
    plugin_base = PluginBase(package=plugin_mount)
    plugin_src_dirs = _get_plugin_src_dirs(plugin_base_dir)
    return plugin_base.make_plugin_source(searchpath=plugin_src_dirs)


def _get_plugin_src_dirs(base_dir):
    plug_in_base_path = Path(get_src_dir(), base_dir)
    plugin_dirs = get_dirs_in_dir(str(plug_in_base_path))
    plugins = []
    for plugin_path in plugin_dirs:
        # Ignore cache directories
        if Path(plugin_path).name == '__pycache__':
            continue

        plugin_code_dir = Path(plugin_path, 'code')
        if plugin_code_dir.is_dir():
            plugins.append(str(plugin_code_dir))
        else:
            logging.warning(f'Plugin has no code directory: {plugin_path}')
    return plugins
