'''
This plugin mounts filesystem images and extracts their content
'''

import re
from tempfile import TemporaryDirectory
from time import sleep

from common_helper_process import (
    execute_shell_command, execute_shell_command_get_return_code
)
from fact_helper_file import get_file_type_from_path

NAME = 'genericFS'
MIME_PATTERNS = ['generic/fs', 'filesystem/cramfs', 'filesystem/romfs', 'filesystem/btrfs', 'filesystem/ext2',
                 'filesystem/ext3', 'filesystem/ext4', 'filesystem/dosmbr', 'filesystem/hfs',
                 'filesystem/jfs', 'filesystem/minix', 'filesystem/reiserfs', 'filesystem/udf', 'filesystem/xfs', 'filesystem/fat', 'filesystem/ntfs']
VERSION = '0.5'
TYPES = {
    'filesystem/cramfs': 'cramfs', 'filesystem/romfs': 'romfs', 'filesystem/btrfs': 'btrfs',
    'filesystem/minix': 'minix', 'filesystem/reiserfs': 'reiserfs', 'filesystem/jfs': 'jfs',
    'filesystem/udf': 'udf', 'filesystem/xfs': 'xfs'
}


def unpack_function(file_path, tmp_dir):
    mime_type = get_file_type_from_path(file_path)['mime']

    if mime_type == 'filesystem/dosmbr':
        output = _mount_from_boot_record(file_path, tmp_dir)
    else:
        output = _mount_single_filesystem(file_path, mime_type, tmp_dir)

    return {'output': output}


def _mount_single_filesystem(file_path, mime_type, tmp_dir):
    type_parameter = '-t {}'.format(TYPES[mime_type]) if mime_type in TYPES else ''
    mount_dir = TemporaryDirectory()
    output = execute_shell_command(
        'sudo mount {} -v -o ro,loop {} {}'.format(type_parameter, file_path, mount_dir.name))
    output += execute_shell_command('sudo cp -av {}/* {}/'.format(mount_dir.name, tmp_dir))
    output += execute_shell_command('sudo umount -v {}'.format(mount_dir.name))
    mount_dir.cleanup()
    return output


def _mount_from_boot_record(file_path, tmp_dir):
    output, return_code = execute_shell_command_get_return_code('sudo kpartx -a -v {}'.format(file_path))
    sleep(1)  # Necessary since initialization of special devices seem to take some time
    if not return_code == 0:
        return 'Failed to mount master boot record image:\n{}'.format(output)

    loop_devices = _extract_loop_devices(output)

    with TemporaryDirectory() as mount_dir:
        for index, loop_device in enumerate(loop_devices):
            output += _process_loop_device(loop_device, mount_dir, tmp_dir, index)

    if loop_devices:
        # Bug in kpartx doesn't allow -d to work on long file names (as in /storage/path/<prefix>/<sha_hash>_<length>)
        # thus "host" loop device is used instead of filename
        k_output, return_code = execute_shell_command_get_return_code('sudo kpartx -d -v {}'.format(_get_host_loop(loop_devices)))
        execute_shell_command('sudo losetup -d {}'.format(_get_host_loop(loop_devices)))
        output += k_output
        return output

    return output


def _process_loop_device(loop_device, mount_point, target_directory, index):
    output = execute_shell_command('sudo mount -o ro -v /dev/mapper/{} {}'.format(loop_device, mount_point))
    output += execute_shell_command('sudo cp -av {}/ {}/partition_{}/'.format(mount_point, target_directory, index))
    output += execute_shell_command('sudo umount -v {}'.format(mount_point))
    return output


def _extract_loop_devices(kpartx_output):
    return re.findall(r'.*(loop\d{1,2}p\d{1,2})\s.*', kpartx_output)


def _get_host_loop(devices):
    return '/dev/{}'.format(re.findall(r'(loop\d{1,2})', devices[0])[0])


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
