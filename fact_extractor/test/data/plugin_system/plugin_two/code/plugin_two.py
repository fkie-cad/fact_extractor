from plugins.base_class import UnpackingPlugin


class UnpackerTwo(UnpackingPlugin):
    NAME = 'plugin_two'
    VERSION = '0.0.1'
    MIME_PATTERNS = ('test/123',)

    def unpack_file(self, file_path, tmp_dir):
        pass
