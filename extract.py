#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

docker_container = 'fkiecad/fact_extractor'
input_file = '/home/dorp/container'
target_directory = '/tmp/target'


tmpdir = TemporaryDirectory()
tmp = tmpdir.name

for subpath in ['files', 'reports', 'input']:
    Path(tmp, subpath).mkdir()

shutil.copy(input_file, str(Path(tmp, 'input', Path(input_file).name)))

subprocess.run('docker run --rm -v {}:/tmp/extractor -v /dev:/dev --privileged {}'.format(tmp, docker_container), shell=True)

shutil.copytree(str(Path(tmp, 'files')), target_directory)

try:
    tmpdir.cleanup()
except PermissionError:
    subprocess.run('sudo rm -rf {}'.format(tmpdir.name), shell=True)
    tmpdir.cleanup()
