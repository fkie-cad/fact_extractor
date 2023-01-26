import logging
import os
from getpass import getuser
from pathlib import Path
from tempfile import TemporaryDirectory

from common_helper_process import execute_shell_command_get_return_code

from helperFunctions.install import (apt_install_packages, apt_remove_packages, gcc_is_new, install_github_project,
                                     InstallationError, is_virtualenv, OperateInDirectory, pip_install_packages)

BIN_DIR = Path(__file__).parent.parent / 'bin'

CFLAGS = '-fcommon' if gcc_is_new() else ''
DEPENDENCIES = {
    # Ubuntu
    'bionic': {
        'apt': [
            # binwalk
            'libqt4-opengl',
            'python3-pyqt4',
            'python3-pyqt4.qtopengl',
            'libcapstone3',
            # patool and unpacking backends
            'openjdk-8-jdk'
        ]
    },
    'focal': {
        'apt': [
            # binwalk
            'libqt5opengl5',
            'python3-pyqt5',
            'python3-pyqt5.qtopengl',
            'libcapstone3',
            # patool and unpacking backends
            'openjdk-16-jdk'
        ]
    },
    'jammy': {
        'apt': [
            # binwalk
            'libqt5opengl5',
            'python3-pyqt5',
            'python3-pyqt5.qtopengl',
            'libcapstone4',
            # patool and unpacking backends
            'openjdk-19-jdk'
        ]
    },
    # Debian
    'buster': {
        'apt': [
            # binwalk
            'libqt4-opengl',
            'python3-pyqt4',
            'python3-pyqt4.qtopengl',
            'libcapstone3',
            # patool and unpacking backends
            'openjdk-8-jdk'
        ]
    },
    'bullseye': {
        'apt': [
            # binwalk
            'libqt5opengl5',
            'python3-pyqt5',
            'python3-pyqt5.qtopengl',
            'libcapstone3',
            # patool and unpacking backends
            'openjdk-14-jdk'
        ]
    },
    # Packages common to all platforms
    'common': {
        'apt': [
            'libjpeg-dev',
            'liblzma-dev',
            'liblzo2-dev',
            'zlib1g-dev',
            'unzip',
            'libffi-dev',
            'libfuzzy-dev',
            'fakeroot',
            'python3-opengl',
            # binwalk
            'mtd-utils',
            'gzip',
            'bzip2',
            'tar',
            'arj',
            'lhasa',
            'cabextract',
            'cramfsswap',
            'squashfs-tools',
            'zlib1g-dev',
            'liblzma-dev',
            'liblzo2-dev',
            'xvfb',
            'libcapstone-dev',
            # patool and unpacking backends
            'lrzip',
            'cpio',
            'unadf',
            'rpm2cpio',
            'lzop',
            'lhasa',
            'cabextract',
            'zpaq',
            'libchm-dev',
            'arj',
            'xdms',
            'rzip',
            'lzip',
            'unalz',
            'unrar',
            'unzip',
            'gzip',
            'nomarch',
            'flac',
            'unace',
            'sharutils',
            'unar',
            # Freetz
            'bison',
            'flex',
            'gettext',
            'libtool-bin',
            'libtool',
            'libacl1-dev',
            'libcap-dev',
            'libc6-dev-i386',
            'lib32ncurses5-dev',
            'gcc-multilib',
            'lib32stdc++6',
            'gawk',
            'pkg-config',
            # android sparse image
            'simg2img',
        ],
        'pip3': [
            'pluginbase',
            'git+https://github.com/armbues/python-entropy',  # To be checked. Original dependency was deleted.
            'git+https://github.com/fkie-cad/common_helper_unpacking_classifier.git',
            'git+https://github.com/fkie-cad/fact_helper_file.git',
            'patool',
            'archmage',
            # binwalk
            'git+https://github.com/ReFirmLabs/binwalk@v2.3.2',
            'pyqtgraph',
            'capstone',
            'cstruct==1.8',
            'python-lzo',
            'numpy',
            'scipy',
            'git+https://github.com/jrspruitt/ubi_reader@v0.6.3-master',  # pinned as broken currently
            # dji
            'pycrypto',
            # hp / raw
            'git+https://github.com/fkie-cad/common_helper_extraction.git',
            # intel_hex
            'intelhex',
            # linuxkernel
            'lz4',
            'git+https://github.com/marin-m/vmlinux-to-elf',
            # mikrotik
            'npkPy',
            # sevenz
            'git+https://github.com/fkie-cad/common_helper_passwords.git',
            # srec
            'bincopy',
            # uboot
            'extract-dtb',
        ],
        'github': [
            ('kartone/sasquatch', [f"sed 's/ -Werror / {CFLAGS} /g' -i patches/patch0.txt", './build.sh']),
            ('svidovich/jefferson-3', ['python3 setup.py install' if is_virtualenv() else 'sudo -EH python3 setup.py install']),
            (
                'rampageX/firmware-mod-kit',
                ['(cd src && make)', 'cp src/yaffs2utils/unyaffs2 src/untrx src/tpl-tool/src/tpl-tool ../../bin/']
            )
        ]
    }
}


def install_dependencies(dependencies):
    apt = dependencies.get('apt', [])
    pip3 = dependencies.get('pip3', [])
    github = dependencies.get('github', [])
    apt_install_packages(*apt)
    pip_install_packages(*pip3)
    for repo in github:
        install_github_project(*repo)


def main(distribution):
    # removes due to compatibility reasons
    try:
        apt_remove_packages('python-lzma')
    except InstallationError:
        logging.debug('python-lzma not removed because present already')

    # install dependencies
    install_dependencies(DEPENDENCIES['common'])
    install_dependencies(DEPENDENCIES[distribution])

    # installing freetz
    _install_freetz()

    # install plug-in dependencies
    _install_plugins()

    # configure environment
    _edit_sudoers()

    return 0


def _edit_sudoers():
    logging.info('add rules to sudo...')
    username = os.environ['USER']
    sudoers_content = '\n'.join((f'{username}\tALL=NOPASSWD: {command}' for command in (
        '/sbin/kpartx', '/sbin/losetup', '/bin/mount', '/bin/umount', '/bin/mknod', '/usr/local/bin/sasquatch', '/bin/rm', '/bin/cp', '/bin/dd', '/bin/chown'
    )))
    Path('/tmp/fact_overrides').write_text(f'{sudoers_content}\n')
    chown_output, chown_code = execute_shell_command_get_return_code('sudo chown root:root /tmp/fact_overrides')
    mv_output, mv_code = execute_shell_command_get_return_code('sudo mv /tmp/fact_overrides /etc/sudoers.d/fact_overrides')
    if not chown_code == mv_code == 0:
        raise InstallationError('Editing sudoers file did not succeed\n{chown_output}\n{mv_output}')


def _install_freetz():
    logging.info('Installing FREETZ')
    current_user = getuser()
    with TemporaryDirectory(prefix='fact_freetz') as build_directory:
        with OperateInDirectory(build_directory):
            os.umask(0o022)
            install_github_project('Freetz/freetz', [
                'sudo useradd -M makeuser',
                'sudo ln -s $(which python3) ./python',
                f'sudo chown -R makeuser {build_directory}',
                'sudo su makeuser -c "export PATH=$(pwd):$PATH && umask 0022 && make -j$(nproc) tools"',
                f'sudo chmod -R 777 {build_directory}',
                f'sudo chown -R {current_user} {build_directory}',
                'cp tools/find-squashfs tools/unpack-kernel tools/freetz_bin_functions tools/unlzma tools/sfk '
                f'tools/unsquashfs4-avm-be tools/unsquashfs4-avm-le tools/unsquashfs3-multi {BIN_DIR}',
                'sudo userdel makeuser'
            ])


def _install_plugins():
    logging.info('Installing plugins')
    find_output, return_code = execute_shell_command_get_return_code('find ../plugins -iname "install.sh"')
    if return_code != 0:
        raise InstallationError('Error retrieving plugin installation scripts')
    for install_script in find_output.splitlines(keepends=False):
        logging.info(f'Running {install_script}')
        shell_output, return_code = execute_shell_command_get_return_code(install_script)
        if return_code != 0:
            raise InstallationError(f'Error in installation of {Path(install_script).parent.name} plugin\n{shell_output}')
