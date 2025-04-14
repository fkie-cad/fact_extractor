"""
This plugin does not unpack any files.
"""

from plugins.base_class import UnpackingPlugin


class NopUnpacker(UnpackingPlugin):
    NAME = 'NOP'
    MIME_PATTERNS = ('generic/nop', 'inode/symlink')
    VERSION = '0.1'

    def unpack_file(self, *_, **__):
        """
        file_path specifies the input file.
        tmp_dir should be used to store the extracted files.
        Optional: Return a dict with meta information
        """
        return {'info': 'unpacking skipped'}
