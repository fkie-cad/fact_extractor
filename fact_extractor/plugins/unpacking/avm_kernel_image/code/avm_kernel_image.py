from common_helper_process.fail_safe_subprocess import execute_shell_command
from pathlib import Path
from fact_extractor.helperFunctions.file_system import get_fact_bin_dir


NAME = 'avm_kernel_image'
MIME_PATTERNS = ['linux/avm-kernel-image-v1', 'linux/avm-kernel-image-v2']
VERSION = '0.2'


FIND_SQUASHFS_TOOL_PATH = Path(get_fact_bin_dir()) / 'find-squashfs'
UNPACK_KERNEL_TOOL_PATH = Path(get_fact_bin_dir()) / 'unpack-kernel'


def unpack_function(file_path, tmp_dir):

    sqfs_output = _extract_squashfs(file_path, tmp_dir)
    meta_dict = {'01_sqfs_extraction': sqfs_output}
    if 'no squashfs signature found' in sqfs_output:
        kernel_extraction_output = _extract_kernel_image(file_path, tmp_dir)
        meta_dict['02_kernel_extraction'] = kernel_extraction_output
    return meta_dict


def _extract_squashfs(file_path, tmp_dir):
    return execute_shell_command('cd {} && {} {}'.format(tmp_dir, FIND_SQUASHFS_TOOL_PATH, file_path))


def _extract_kernel_image(file_path, tmp_dir):
    return execute_shell_command('{} {} {}/kernel_decompressed.img'.format(UNPACK_KERNEL_TOOL_PATH, file_path, tmp_dir))


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
