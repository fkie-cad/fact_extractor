from common_helper_process import execute_shell_command_get_return_code
from getpass import getuser
import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from helperFunctions.install import (
    InstallationError, apt_install_packages, apt_remove_packages,
    install_github_project, pip2_remove_packages,
    pip3_install_packages, OperateInDirectory
)
from contextlib import suppress


BIN_DIR = Path(__file__).parent.parent / 'bin'

DEPENDENCIES = {
    # Ubuntu
    'xenial': {
        'apt': [
            # binwalk
            'cramfsprogs',
            'libqt4-opengl',
            'python3-pyqt4',
            'python3-pyqt4.qtopengl',
            'libcapstone3',
            # patool and unpacking backends
            'zoo',
            'openjdk-8-jdk'
        ]
    },
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
            'openjdk-14-jdk'
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
    'kali': {
        'apt': [
            'p7zip-full',
            'libqt5opengl5',
            'python3-pyqt5',
            'python3-pyqt5.qtopengl',
            'openjdk-11-jdk',
            'firmware-mod-kit',
            'libcapstone4'
        ]
    },
    # Packages common to all plateforms
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
            'pkg-config'
        ],
        'pip3': [
            'pluginbase',
            'git+https://github.com/armbues/python-entropy',  # To be checked. Original dependency was deleted.
            'git+https://github.com/fkie-cad/common_helper_unpacking_classifier.git',
            'git+https://github.com/fkie-cad/fact_helper_file.git',
            'patool',
            'archmage',
            # binwalk
            'pyqtgraph',
            'capstone',
            'cstruct',
            'python-lzo',
            'numpy',
            'scipy',
            'git+https://github.com/jrspruitt/ubi_reader@v0.6.3-master'  # pinned as broken currently
        ],
        'github': [
            ('devttys0/sasquatch', ['CFLAGS=-fcommon ./build.sh -y']),
            ('ReFirmLabs/binwalk', ['sudo python3 setup.py install']),
            ('svidovich/jefferson-3', ['sudo python3 setup.py install'])
        ]
    }
}


def install_dependencies(dependencies):
    apt = dependencies.get('apt', [])
    pip3 = dependencies.get('pip3', [])
    github = dependencies.get('github', [])
    apt_install_packages(*apt)
    pip3_install_packages(*pip3)
    for repo in github:
        install_github_project(*repo)


def main(distribution):
    # removes due to compatibilty reasons
    try:
        apt_remove_packages('python-lzma')
        pip2_remove_packages('pyliblzma')
    except InstallationError:
        logging.debug('python-lzma not removed because present already')
    with suppress(InstallationError):
        pip2_remove_packages('jefferson')

    # install dependencies
    install_dependencies(DEPENDENCIES['common'])
    install_dependencies(DEPENDENCIES[distribution])

    if distribution == "kali" and os.path.isdir("/opt/firmware-mod-kit"):
        logging.info('Kali Linux - copy binaries from installed firmware-mod-kit ...')
        os.system('cp /opt/firmware-mod-kit/trunk/src/yaffs2utils/unyaffs2 /opt/firmware-mod-kit/trunk/src/untrx /opt/firmware-mod-kit/trunk/src/tpl-tool/src/tpl-tool ../bin/')
    else:
        logging.info('No Kali Linux - install firmware-mod-kit from github')
        install_github_project('rampageX/firmware-mod-kit', ['(cd src && sh configure && make)', 'cp src/yaffs2utils/unyaffs2 src/untrx src/tpl-tool/src/tpl-tool ../../bin/'])

    # installing freetz
    # currently the freetz installation does not work on a recent Kali Linux
    if distribution != "kali":
        _install_freetz()
    else:
        logging.info("Kali linux detected - Not installing Freetz")

    # install plug-in dependencies
    _install_plugins()

    # configure environment
    _edit_sudoers()

    return 0


def _edit_sudoers():
    logging.info('add rules to sudo...')
    username = os.environ['USER']
    sudoers_content = '\n'.join(('{}\tALL=NOPASSWD: {}'.format(username, command) for command in (
        '/sbin/kpartx', '/sbin/losetup', '/bin/mount', '/bin/umount', '/bin/mknod', '/usr/local/bin/sasquatch', '/bin/rm', '/bin/cp', '/bin/dd', '/bin/chown'
    )))
    Path('/tmp/fact_overrides').write_text('{}\n'.format(sudoers_content))
    chown_output, chown_code = execute_shell_command_get_return_code('sudo chown root:root /tmp/fact_overrides')
    mv_output, mv_code = execute_shell_command_get_return_code('sudo mv /tmp/fact_overrides /etc/sudoers.d/fact_overrides')
    if not chown_code == mv_code == 0:
        raise InstallationError('Editing sudoers file did not succeed\n{}\n{}'.format(chown_output, mv_output))


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
                'sudo cp tools/find-squashfs tools/unpack-kernel tools/freetz_bin_functions tools/unlzma tools/sfk '
                f'tools/unsquashfs4-avm-be tools/unsquashfs4-avm-le tools/unsquashfs3-multi {BIN_DIR}',
                'sudo userdel makeuser'
            ])


def _install_plugins():
    logging.info('Installing plugins')
    find_output, return_code = execute_shell_command_get_return_code('find ../plugins -iname "install.sh"')
    if return_code != 0:
        raise InstallationError('Error retrieving plugin installation scripts')
    for install_script in find_output.splitlines(keepends=False):
        logging.info('Running {}'.format(install_script))
        shell_output, return_code = execute_shell_command_get_return_code(install_script)
        if return_code != 0:
            raise InstallationError('Error in installation of {} plugin\n{}'.format(Path(install_script).parent.name, shell_output))
