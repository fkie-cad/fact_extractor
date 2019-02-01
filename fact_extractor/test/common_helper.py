import os

from helperFunctions.fileSystem import get_test_data_dir
from objects.file import FileObject


def create_test_file_object(bin_path='get_files_test/testfile1'):
    fo = FileObject(file_path=os.path.join(get_test_data_dir(), bin_path))
    processed_analysis = {
        'dummy': {'summary': ['sum a', 'file exclusive sum b'], 'content': 'file abcd'},
        'file_type': {'full': 'Not a PE file'},
        'unpacker': {'file_system_flag': False, 'plugin_used': 'unpacker_name'}
    }
    fo.processed_analysis.update(processed_analysis)
    fo.virtual_file_path = fo.get_virtual_file_paths()
    return fo
