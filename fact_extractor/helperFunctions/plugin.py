from __future__ import annotations

import importlib.util
import logging
import sys
from importlib.machinery import SourceFileLoader
from inspect import isclass
from pathlib import Path
from typing import Iterable, Type

from plugins.base_class import UnpackingPlugin

SRC_DIR = Path(__file__).parent.parent
PLUGIN_DIR = SRC_DIR / 'plugins'


def import_plugins(path=PLUGIN_DIR) -> list:
    """Returns a list of modules where each module is an unpacking plugin."""
    plugins = []
    for plugin_file in path.glob('**/code/*.py'):  # type: Path
        if plugin_file.name == '__init__.py':
            continue

        module_name = str(plugin_file.relative_to(SRC_DIR)).replace('/', '.')[: -len('.py')]
        loader = SourceFileLoader(module_name, str(plugin_file))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        plugin_module = importlib.util.module_from_spec(spec)

        sys.modules[spec.name] = plugin_module
        try:
            loader.exec_module(plugin_module)
            plugins.append(plugin_module)
        except Exception as error:  # probably missing dependencies
            sys.modules.pop(spec.name)
            logging.exception(f'Could not import plugin {module_name} due to exception: {error}')

    return plugins


def find_plugin_classes(module) -> Iterable[Type[UnpackingPlugin]]:
    """get all subclasses of UnpackingPlugin from the module"""
    for attr_name in dir(module):
        if attr_name.startswith('_'):
            continue
        attr = getattr(module, attr_name)
        if _is_plugin_class(attr):
            yield attr


def _is_plugin_class(attr) -> bool:
    return attr != UnpackingPlugin and isclass(attr) and issubclass(attr, UnpackingPlugin)
