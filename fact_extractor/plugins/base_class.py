from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type


class PluginError(Exception):
    pass


class UnpackingPlugin(ABC):
    MIME_PATTERNS = ()  # must be overwritten by the subclass
    NAME = 'base'
    VERSION = '0.0.0'

    @abstractmethod
    def unpack_file(self, file_path: str, tmp_dir: str) -> dict:
        """
        Unpack a file `file_path` to `tmp_dir`. Must be implemented by the concrete unpacker subclass!
        The function returns a dictionary with metadata from unpacking the file. The key 'output' is expected and
        its value should contain the output of the used tool or relevant logging messages.

        :param file_path: Path to the file to be unpacked.
        :param tmp_dir: Path to the temporary directory where the file will be unpacked.
        :return: The metadata.
        """

    def validate(self):
        if len(self.MIME_PATTERNS) == 0:
            raise PluginError(f'{self.NAME} is not a valid plugin (no MIME patterns defined)')
        if self.NAME == 'base':
            raise PluginError(f'{self.NAME} is not a valid plugin (no NAME defined)')
        if self.VERSION == '0.0.0':
            raise PluginError(f'{self.NAME} is not a valid plugin (no VERSION defined)')

    @classmethod
    def from_old_module(cls, old_module) -> Type[UnpackingPlugin]:
        """For backwards compatibility with old plugins, create a subclass dynamically."""
        return type(
            f'{old_module.__name__}.Unpacker',
            (cls,),
            {
                'NAME': old_module.NAME,
                'VERSION': old_module.VERSION,
                'MIME_PATTERNS': old_module.MIME_PATTERNS,
                'unpack_file': staticmethod(old_module.unpack_function),
            },
        )
