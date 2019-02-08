import logging
import os
from pathlib import Path

from common_helper_process import execute_shell_command_get_return_code

from helperFunctions.install import apt_remove_packages, apt_install_packages, InstallationError, pip3_install_packages, \
    install_github_project, pip2_install_packages, pip2_remove_packages, OperateInDirectory, load_main_config


def main(distribution):
    # dependencies
    apt_install_packages('python-dev', 'python-setuptools')
    apt_install_packages('libjpeg-dev', 'liblzma-dev', 'liblzo2-dev', 'zlib1g-dev')
    pip3_install_packages('pluginbase', 'entropy')

    apt_install_packages('python-pip')
    # removes due to compatibilty reasons
    apt_remove_packages('python-lzma')
    pip2_remove_packages('pyliblzma')
    apt_install_packages('python-lzma')

    # installing unpacker
    _install_unpacker(distribution == 'xenial')

    # installing common code modules
    pip3_install_packages('git+https://github.com/fkie-cad/common_helper_unpacking_classifier.git')

    # install plug-in dependencies
    _install_plugins()

    # compile custom magic file
    with OperateInDirectory('../mime'):
        cat_output, cat_code = execute_shell_command_get_return_code('cat custom_* > custommime')
        file_output, file_code = execute_shell_command_get_return_code('file -C -m custommime')
        mv_output, mv_code = execute_shell_command_get_return_code('mv -f custommime.mgc ../bin/')
        if any(code != 0 for code in (cat_code, file_code, mv_code)):
            raise InstallationError('Failed to properly compile magic file\n{}'.format('\n'.join((cat_output, file_output, mv_output))))
        Path('custommime').unlink()

    # configure environment
    _edit_sudoers()

    return 0


def _edit_sudoers():
    logging.info('add rules to sudo...')
    username = os.environ['USER']
    sudoers_content = '\n'.join(('{}\tALL=NOPASSWD: {}'.format(username, command) for command in ('/bin/mount', '/bin/umount', '/bin/mknod', '/usr/local/bin/sasquatch', '/bin/rm', '/bin/cp', '/bin/dd', '/bin/chown')))
    Path('/tmp/fact_overrides').write_text('{}\n'.format(sudoers_content))
    chown_output, chown_code = execute_shell_command_get_return_code('sudo chown root:root /tmp/fact_overrides')
    mv_output, mv_code = execute_shell_command_get_return_code('sudo mv /tmp/fact_overrides /etc/sudoers.d/fact_overrides')
    if not chown_code == mv_code == 0:
        raise InstallationError('Editing sudoers file did not succeed\n{}\n{}'.format(chown_output, mv_output))


def _install_unpacker(xenial):
    apt_install_packages('fakeroot')
    # ---- sasquatch unpacker ----
    # Original: devttys0/sasquatch
    # Ubuntu 18.04 compatiblity issue in original source. Fixed in this fork:
    install_github_project('kartone/sasquatch', ['./build.sh'])
    # ubi_reader
    pip2_install_packages('python-lzo')
    install_github_project('jrspruitt/ubi_reader', ['sudo python2 setup.py install --force'])
    # binwalk
    if xenial:
        apt_install_packages('cramfsprogs')
    apt_install_packages('libqt4-opengl', 'python3-opengl', 'python3-pyqt4', 'python3-pyqt4.qtopengl', 'mtd-utils',
                         'gzip', 'bzip2', 'tar', 'arj', 'lhasa', 'cabextract', 'cramfsswap', 'squashfs-tools',
                         'zlib1g-dev', 'liblzma-dev', 'liblzo2-dev', 'liblzo2-dev', 'xvfb')
    apt_install_packages('libcapstone3', 'libcapstone-dev')
    pip3_install_packages('pyqtgraph', 'capstone', 'cstruct', 'python-lzo', 'numpy', 'scipy')
    install_github_project('sviehb/jefferson', ['sudo python3 setup.py install'])
    _install_stuffit()
    install_github_project('devttys0/binwalk', ['sudo python3 setup.py install --force'])
    # patool and unpacking backends
    pip2_install_packages('patool')
    pip3_install_packages('patool')
    apt_install_packages('openjdk-8-jdk')
    if xenial:
        apt_install_packages('zoo')
    apt_install_packages('lrzip', 'cpio', 'unadf', 'rpm2cpio', 'lzop', 'lhasa', 'cabextract', 'zpaq', 'archmage', 'arj',
                         'xdms', 'rzip', 'lzip', 'unalz', 'unrar', 'unzip', 'gzip', 'nomarch', 'flac', 'unace',
                         'sharutils')
    apt_install_packages('unar')
    # firmware-mod-kit
    install_github_project('rampageX/firmware-mod-kit', ['git checkout 5e74fe9dd', '(cd src && sh configure && make)',
                                                         'cp src/yaffs2utils/unyaffs2 src/untrx src/tpl-tool/src/tpl-tool ../../bin/'])

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
    _, wget_code = execute_shell_command_get_return_code('wget -O - http://web.archive.org/web/20060205025441/http://www.stuffit.com/downloads/files/stuffit520.611linux-i386.tar.gz | tar -zxv')
    if wget_code == 0:
        _, cp_code = execute_shell_command_get_return_code('sudo cp bin/unstuff /usr/local/bin/')
    else:
        cp_code = 255
    _, rm_code = execute_shell_command_get_return_code('rm -fr bin doc man')
    if not all(code == 0 for code in (wget_code, cp_code, rm_code)):
        raise InstallationError('Error in installation of unstuff')
