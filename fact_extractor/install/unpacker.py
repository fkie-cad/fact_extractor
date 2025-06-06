import hashlib
import logging
import os
import platform
from getpass import getuser
from pathlib import Path
from shlex import split
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory

from common_helper_process import execute_shell_command_get_return_code

from helperFunctions.install import (
    InstallationError,
    OperateInDirectory,
    apt_install_packages,
    apt_remove_packages,
    install_github_project,
    load_requirements_file,
    pip_install_packages,
)

BIN_DIR = Path(__file__).parent.parent / 'bin'

APT_DEPENDENCIES = {
    # Packages common to all platforms
    'libjpeg-dev',
    'liblzma-dev',
    'liblzo2-dev',
    'zlib1g-dev',
    'unzip',
    'libffi-dev',
    'libfuzzy-dev',
    'fakeroot',
    'python3-opengl',
    # patool
    'arc',
    'archmage',
    'arj',
    'binutils',
    'bzip2',
    'cabextract',
    'clzip',
    'cpio',
    'flac',
    'genisoimage',
    'lbzip2',
    'lhasa',
    'libarchive-tools',
    'lrzip',
    'lz4',
    'lzip',
    'lzop',
    'ncompress',
    'nomarch',
    # FixMe: p7zip-full installed in 7z plugin
    'pbzip2',
    'pdlzip',
    'plzip',
    'rpm2cpio',
    'rzip',
    'sharutils',
    'tar',
    'unace',
    'unalz',
    'unar',
    'xdms',
    'zip',
    'zopfli',
    'zpaq',
    'zstd',
    # Freetz
    'autoconf',
    'automake',
    'bison',
    'flex',
    'g++',
    'gawk',
    'gcc',
    'gettext',
    'file',
    'libacl1-dev',
    'libcap-dev',
    'libncurses5-dev',
    'libsqlite3-dev',
    'libtool-bin',
    'libzstd-dev',
    'make',
    'pkg-config',
    'subversion',
    'wget',
    # android sparse image
    'android-sdk-libsparse-utils',
    # 7z
    'yasm',
    # unblob
    'e2fsprogs',
    'libhyperscan-dev',
    'lziprecover',
    # boschtool
    'libicu-dev',
}
GITHUB_DEPENDENCIES = [
    (
        'rampageX/firmware-mod-kit',
        [
            '(cd src && make untrx && make -C tpl-tool/src && make -C yaffs2utils)',
            f'cp src/untrx src/yaffs2utils/unyaffs2 src/tpl-tool/src/tpl-tool {BIN_DIR}',
        ],
    ),
    (
        'openwrt/firmware-utils',
        [
            '(cd src && '
            'gcc -c -o buffalo-enc.o buffalo-enc.c -I./ && '
            'gcc -c -o buffalo-lib.o buffalo-lib.c -I./ && '
            'gcc -o buffalo-enc buffalo-enc.o buffalo-lib.o)',
            f'cp src/buffalo-enc {BIN_DIR}',
        ],
    ),
]
PIP_DEPENDENCY_FILE = Path(__file__).parent.parent.parent / 'requirements-unpackers.txt'
if platform.machine() == 'x86_64':
    EXTERNAL_DEB_DEPS = [
        # zoo
        (
            'zoo_2.10-28_amd64.deb',
            'http://launchpadlibrarian.net/230277773',
            '953f4f94095ef3813dfd30c8977475c834363aaabce15ab85ac5195e52fd816a',
        ),
        # sasquatch
        (
            'sasquatch_1.0_amd64.deb',
            'https://github.com/onekey-sec/sasquatch/releases/download/sasquatch-v4.5.1-4',
            'bb211daf90069a43b7d5e76f136766a8542a5328015773e9b8be87541b307b60',
        ),
    ]
elif platform.machine() == 'aarch64':
    EXTERNAL_DEB_DEPS = [
        # zoo
        (
            'zoo_2.10-28_arm64.deb',
            'http://ports.ubuntu.com/pool/universe/z/zoo',
            'e6600d4e878eddd18d1353664fae9bee015a8f9206aa62d2c9bfa070fe4cb7b3',
        ),
        # sasquatch
        (
            'sasquatch_1.0_arm64.deb',
            'https://github.com/onekey-sec/sasquatch/releases/download/sasquatch-v4.5.1-4',
            'fb281906a25667414e8b6aff96b49ceb227519122a7844bbc8166f2b6a59554a',
        ),
    ]


def check_mod_kit_installed() -> bool:
    return all((Path(__file__).parent.parent / 'bin' / tool).exists() for tool in ['tpl-tool', 'untrx', 'unyaffs2'])


def install_github_dependencies():
    for repo in GITHUB_DEPENDENCIES:
        if repo[0].endswith('firmware-mod-kit') and check_mod_kit_installed():
            logging.info('Skipping firmware-mod-kit since it is already installed')
            continue
        install_github_project(*repo)


def main():
    # removes due to compatibility reasons
    try:
        apt_remove_packages('python-lzma')
    except InstallationError:
        logging.debug('python-lzma not removed because present already')

    # install dependencies
    apt_install_packages(*APT_DEPENDENCIES)
    pip_install_packages(*load_requirements_file(PIP_DEPENDENCY_FILE))
    install_github_dependencies()

    # installing freetz
    if platform.machine() == 'x86_64':
        _install_freetz()

    # install plug-in dependencies
    _install_plugins()
    _install_external_deb_deps()

    # configure environment
    _edit_sudoers()

    return 0


def _edit_sudoers():
    logging.info('add rules to sudo...')
    username = getuser()
    sudoers_content = '\n'.join(
        f'{username}\tALL=NOPASSWD: {command}'
        for command in (
            '/sbin/kpartx',
            '/sbin/losetup',
            '/bin/mount',
            '/bin/umount',
            '/bin/mknod',
            '/usr/bin/sasquatch',
            '/bin/rm',
            '/bin/cp',
            '/bin/dd',
            '/bin/chown',
        )
    )
    Path('/tmp/fact_overrides').write_text(f'{sudoers_content}\n', encoding='utf-8')
    _, chown_code = execute_shell_command_get_return_code('sudo chown root:root /tmp/fact_overrides')
    _, mv_code = execute_shell_command_get_return_code('sudo mv /tmp/fact_overrides /etc/sudoers.d/fact_overrides')
    if not chown_code == mv_code == 0:
        raise InstallationError('Editing sudoers file did not succeed\n{chown_output}\n{mv_output}')


def _install_external_deb_deps():
    """
    install deb packages that aren't available through Debian/Ubuntu package sources
    """
    with TemporaryDirectory(prefix='patool') as build_directory, OperateInDirectory(build_directory):
        for file_name, url, sha256 in EXTERNAL_DEB_DEPS:
            try:
                run(split(f'wget {url}/{file_name}'), check=True, env=os.environ)
                if not _sha256_hash_file(Path(file_name)) == sha256:
                    raise InstallationError(f'Wrong file hash: {file_name}')
                run(split(f'sudo dpkg -i {file_name}'), capture_output=True, check=True)
            except CalledProcessError as error:
                raise InstallationError(f'Error during {file_name} unpacker installation') from error


def _sha256_hash_file(file_path: Path) -> str:
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def _freetz_is_already_installed():
    return all(
        (Path(__file__).parent.parent / 'bin' / tool).exists()
        for tool in [
            'find-squashfs',
            'unpack-kernel',
            'freetz_bin_functions',
            'unlzma',
            'sfk',
            'unsquashfs4-avm-be',
            'unsquashfs4-avm-le',
            'unsquashfs3-multi',
        ]
    )


def _install_freetz():
    if _freetz_is_already_installed():
        logging.info('Skipping FREETZ installation (already installed)')
        return

    logging.info('Installing FREETZ')
    current_user = getuser()
    freetz_build_config = Path(__file__).parent / 'freetz.config'
    with TemporaryDirectory(prefix='fact_freetz') as build_directory, OperateInDirectory(build_directory):
        os.umask(0o022)
        install_github_project(
            'Freetz-NG/freetz-ng',
            [
                # add user only if it does not exist to fix issues with re-running the installation after an error
                'id -u makeuser || sudo useradd -M makeuser',
                'sudo mkdir -p /home/makeuser',
                'sudo chown -R makeuser /home/makeuser',
                f'cp {freetz_build_config} ./.config',
                f'sudo chown -R makeuser {build_directory}',
                'sudo su makeuser -c "make -j$(nproc) tools"',
                f'sudo chmod -R 777 {build_directory}',
                f'sudo chown -R {current_user} {build_directory}',
                'cp tools/find-squashfs tools/unpack-kernel tools/freetz_bin_functions tools/unlzma tools/sfk '
                f'tools/unsquashfs4-avm-be tools/unsquashfs4-avm-le tools/unsquashfs3-multi {BIN_DIR}',
                'sudo userdel makeuser',
            ],
        )


def _install_plugins():
    logging.info('Installing plugins')
    find_output, return_code = execute_shell_command_get_return_code('find ../plugins -iname "install.sh"')
    if return_code != 0:
        raise InstallationError('Error retrieving plugin installation scripts')
    for install_script in find_output.splitlines(keepends=False):
        logging.info(f'Running {install_script}')
        shell_output, return_code = execute_shell_command_get_return_code(install_script)
        if return_code != 0:
            raise InstallationError(
                f'Error in installation of {Path(install_script).parent.name} plugin\n{shell_output}'
            )
