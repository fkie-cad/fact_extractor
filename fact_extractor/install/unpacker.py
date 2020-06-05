from common_helper_process import execute_shell_command_get_return_code
from getpass import getuser
import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from helperFunctions.install import (
    InstallationError, apt_install_packages, apt_remove_packages,
    install_github_project, pip2_install_packages, pip2_remove_packages,
    pip3_install_packages, OperateInDirectory
)


BIN_DIR = Path(__file__).parent.parent / 'bin'

DEPENDENCIES = {
    # Ubuntu
    'xenial': {
        'apt': [
            'python-lzma',
            # binwalk
            'cramfsprogs',
            'libqt4-opengl',
            'python3-pyqt4',
            'python3-pyqt4.qtopengl',
            # patool and unpacking backends
            'zoo',
            'openjdk-8-jdk'
        ],
        'pip2': [
            # ubi_reader
            'python-lzo',
            # patool
            'patool'
        ]
    },
    'bionib': {
        'apt': [
            'python-lzma',
            # binwalk
            'libqt4-opengl',
            'python3-pyqt4',
            'python3-pyqt4.qtopengl',
            # patool and unpacking backends
            'openjdk-8-jdk'
        ],
        'pip2': [
            # ubi_reader
            'python-lzo',
            # patool
            'patool'
        ]
    },
    'focal': {
        'apt': [
            # binwalk
            'libqt5opengl5',
            'python3-pyqt5',
            'python3-pyqt5.qtopengl',
            # patool and unpacking backends
            'patool',
            'openjdk-14-jdk'
        ]
    },
    # Debian
    'buster': {
        'apt': [
            'python-lzma',
            # binwalk
            'libqt4-opengl',
            'python3-pyqt4',
            'python3-pyqt4.qtopengl',
            # patool and unpacking backends
            'openjdk-8-jdk'
        ],
        'pip2': [
            # ubi_reader
            'python-lzo',
            # patool
            'patool'
        ]
    },
    'bullseye': {
        'apt': [
            # binwalk
            'libqt5opengl5',
            'python3-pyqt5',
            'python3-pyqt5.qtopengl',
            # patool and unpacking backends
            'patool',
            'openjdk-14-jdk'
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
            'liblzo2-dev',
            'xvfb',
            'libcapstone3',
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
            'archmage',
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
            # binwalk
            'pyqtgraph',
            'capstone',
            'cstruct',
            'python-lzo',
            'numpy',
            'scipy'
        ]
    }
}


def install_dependencies(dependencies):
    apt = dependencies.get('apt', [])
    pip2 = dependencies.get('pip2', [])
    pip3 = dependencies.get('pip3', [])
    apt_install_packages(*apt)
    pip2_install_packages(*pip2)
    pip3_install_packages(*pip3)


def main(distribution):
    # removes due to compatibilty reasons
    try:
        apt_remove_packages('python-lzma')
        pip2_remove_packages('pyliblzma')
    except InstallationError:
        logging.debug('python-lzma not removed because present already')

    # install dependencies
    install_dependencies(DEPENDENCIES['common'])
    install_dependencies(DEPENDENCIES[distribution])

    # installing unpacker
    _install_unpacker(distribution)

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


def _install_unpacker(distribution):
    # sasquatch unpacker
    install_github_project('kartone/sasquatch', ['./build.sh'])

    # ubi_reader
    install_github_project('jrspruitt/ubi_reader', ['sudo python2 setup.py install --force'])

    install_github_project('sviehb/jefferson', ['sudo python3 setup.py install'])
    _install_stuffit()
    install_github_project('dorpvom/binwalk', ['sudo python3 setup.py install --force'])

    # firmware-mod-kit
    # Removed 'git checkout 5e74fe9dd'
    install_github_project('rampageX/firmware-mod-kit', ['(cd src && sh configure && make)',
                                                         'cp src/yaffs2utils/unyaffs2 src/untrx src/tpl-tool/src/tpl-tool ../../bin/'])
    _install_freetz(distribution)


def _install_freetz(distribution):
    logging.info('Installing FREETZ')
    current_user = getuser()
    with TemporaryDirectory(prefix='fact_freetz') as build_directory:
        with OperateInDirectory(build_directory):
            os.umask(0o022)
            install_github_project('Freetz/freetz', ['sudo useradd -M makeuser',
                                                     'sudo chown -R makeuser {}'.format(build_directory),
                                                     'sudo su makeuser -c "umask 0022 && make -j$(nproc) tools"',
                                                     'sudo chmod -R 777 {}'.format(build_directory),
                                                     'sudo chown -R {} {}'.format(current_user, build_directory),
                                                     'cp tools/find-squashfs tools/unpack-kernel tools/unlzma tools/freetz_bin_functions\
                                                     tools/sfk tools/unsquashfs4-avm-be tools/unsquashfs4-avm-le tools/unsquashfs3-multi\
                                                     {}'.format(BIN_DIR),
                                                     'sudo userdel makeuser'])


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


def _install_stuffit():
    logging.info('Installing stuffit')
    _, wget_code = execute_shell_command_get_return_code('wget -O - http://my.smithmicro.com/downloads/files/stuffit520.611linux-i386.tar.gz | tar -zxv')
    if wget_code == 0:
        _, cp_code = execute_shell_command_get_return_code('sudo cp bin/unstuff /usr/local/bin/')
    else:
        cp_code = 255
    _, rm_code = execute_shell_command_get_return_code('rm -fr bin doc man')
    if not all(code == 0 for code in (wget_code, cp_code, rm_code)):
        raise InstallationError('Error in installation of unstuff')
