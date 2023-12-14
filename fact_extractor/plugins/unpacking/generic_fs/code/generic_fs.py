'''
This plugin mounts filesystem images and extracts their content
'''
import re
from shlex import split
from subprocess import run, PIPE, STDOUT
from tempfile import TemporaryDirectory
from time import sleep

from fact_helper_file import get_file_type_from_path
from helperFunctions.shell_utils import shell_escape_string

NAME = 'genericFS'
MIME_PATTERNS = [
    'filesystem/btrfs', 'filesystem/dosmbr', 'filesystem/f2fs', 'filesystem/jfs', 'filesystem/minix',
    'filesystem/reiserfs', 'filesystem/romfs', 'filesystem/udf', 'filesystem/xfs', 'generic/fs',
]
VERSION = '0.6.1'
TYPES = {
    'filesystem/btrfs': 'btrfs',
    'filesystem/f2fs': 'f2fs',
    'filesystem/jfs': 'jfs',
    'filesystem/minix': 'minix',
    'filesystem/reiserfs': 'reiserfs',
    'filesystem/romfs': 'romfs',
    'filesystem/udf': 'udf',
    'filesystem/xfs': 'xfs',
}


def unpack_function(file_path, tmp_dir):
    mime_type = get_file_type_from_path(file_path)['mime']
    if mime_type == 'filesystem/dosmbr':
        output = _mount_from_boot_record(file_path, tmp_dir)
    else:
        output = _mount_single_filesystem(file_path, mime_type, tmp_dir)

    return {'output': output}


def _mount_single_filesystem(file_path, mime_type, tmp_dir):
    type_parameter = f'-t {TYPES[mime_type]}' if mime_type in TYPES else ''
    with TemporaryDirectory() as mount_dir:
        output = _get_output(f'sudo mount {type_parameter} -v -o ro,loop {shell_escape_string(str(file_path))} {mount_dir}')
        output += _get_output(f'sudo cp -av {mount_dir}/* {tmp_dir}/')
        output += _get_output(f'sudo umount -v {mount_dir}')

    if 'unknown filesystem type' in output:
        output += '\nwarning: you may need to install additional kernel modules'
    return output


def _get_output(command: str) -> str:
    environment = {'LANG': 'en_US.UTF-8'}  # use LANG env variable to get unified localization output
    return run(command, shell=True, env=environment, check=False, text=True, stdout=PIPE, stderr=STDOUT).stdout


def _run(command: str):
    run(split(command), check=False)


def _mount_from_boot_record(file_path, tmp_dir):
    output = _get_output(f'sudo kpartx -a -v {shell_escape_string(str(file_path))}')
    sleep(1)  # Necessary since initialization of special devices seem to take some time
    # kpartx may return an error on one partition but others are still loaded correctly.
    loop_devices = _extract_loop_devices(output)

    with TemporaryDirectory() as mount_dir:
        for index, loop_device in enumerate(loop_devices):
            output += _process_loop_device(loop_device, mount_dir, tmp_dir, index)

    if loop_devices:
        # Occasionally device mapping isn't removed correctly and results in losetup -d to fail, so remove explicitly
        for loop_dev in loop_devices:
            _run(f'sudo dmsetup remove /dev/mapper/{loop_dev}')

        # Bug in kpartx doesn't allow -d to work on long file names (as in /storage/path/<prefix>/<sha_hash>_<length>)
        # thus "host" loop device is used instead of filename
        output += _get_output(f'sudo kpartx -d -v {_get_host_loop(loop_devices)}')
        _run(f'sudo losetup -d {_get_host_loop(loop_devices)}')

    return output


def _process_loop_device(loop_device, mount_point, target_directory, index):
    output = _get_output(f'sudo mount -o ro -v /dev/mapper/{loop_device} {mount_point}')
    output += _get_output(f'sudo cp -av {mount_point}/ {target_directory}/partition_{index}/')
    return output + _get_output(f'sudo umount -v {mount_point}')


def _extract_loop_devices(kpartx_output):
    return re.findall(r'.*map (loop\d{1,2}p\d{1,2})\s.*', kpartx_output)


def _get_host_loop(devices):
    device = re.findall(r'(loop\d{1,2})', devices[0])[0]
    return f'/dev/{device}'


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
