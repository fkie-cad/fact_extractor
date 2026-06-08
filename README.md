# FACT extractor

Wraps FACT unpack plugins into standalone utility.
Should be able to extract most of the common container formats.


## Command line usage

Quickest usage if you have docker running:

```sh
docker pull fkiecad/fact_extractor
uv run fact-extractor extract-docker ./relative/or/absolute/path/to/your/file
```

for more options see

```sh
uv run fact-extractor extract-docker --help
```

## Local setup (aka not running through docker)

### Prerequisites

Install system dependencies:

```bash
sudo apt update
sudo apt install -y git libmagic-dev xz-utils
```

Run apt installation (build tools, archive tools, etc.):

```bash
uv run fact-extractor install
```

:warning: For the `generic_fs` unpacker plugin to work with all file system types, you may need to install extra kernel modules

```sh
sudo apt install linux-modules-extra-$(uname -r)
```

The tool can then be run with

```bash
uv run fact-extractor
```

The tool is build with docker in mind.
To that end it extracts all files into a directory specified in the config.
The same directory also contains the metadata report.
Directories are created during installation, if config is changed make sure to recreate the folder structure.
It looks like:

```text
<path_to_data_folder>
├── files
└── reports
```


## Using uv

This project uses [uv](https://github.com/astral-sh/uv) for Python dependency management.
See [the docs](https://docs.astral.sh/uv/getting-started/installation/) for information on how to install and use uv. 

### Common Commands

```bash
# install dependencies (including dev dependencies)
uv sync --extra dev

# install only runtime dependencies
uv sync

# run extractor script
uv run fact-extractor

usage: fact-extractor [-h] [--version] {install,extract-docker,extract-local,server} ...

FACT Extractor - Extractor for the Firmware Analysis and Comparison Tool

positional arguments:
  {install,extract-docker,extract-local,server}
    install             Install system dependencies and packages
    extract-docker      Extract using Docker container
    extract-local       Extract locally without Docker
    server              Run extraction server

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

# Run tests
uv run pytest
```

## Docker

Build the image with

```bash
docker build -t fact_extractor .
```
(Replace `fact_extractor` with own id if you like)

The docker execution was build so that a single shared directory can be used for container input and output.
Prepare a folder on the host system that resembles

```text
<path_to_shared_folder>
├── files
├── input
│   └── firmware_file
└── reports
```

where **firmware_file** is the file you want to unpack.
Run the extraction with

```bash
docker run -v <path_to_shared_folder>:/tmp/extractor -v /dev:/dev --privileged --rm fact_extractor
```
(see above)

:warning: Note that the container is run in privileged mode and shares the /dev folder.
Thus, the container can possibly harm your system in various ways.

## Contribute
The easiest way to contribute is writing your own plugin.
Our Developers Manual can be found [here](https://github.com/fkie-cad/fact_extractor/wiki).

## Acknowledgments
This project is partly financed by [German Federal Office for Information Security (BSI)](https://www.bsi.bund.de) and others.  

## License
```
    Firmware Analysis and Comparison Tool (FACT) extractor
    Copyright (C) 2015-2022  Fraunhofer FKIE

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    Some plug-ins may have different licenses. If so, a license file is provided in the plug-in's folder.
```
