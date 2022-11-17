# FACT extractor

Wraps FACT unpack plugins into standalone utility.
Should be able to extract most of the common container formats.


## Command line usage

Quickest usage if you have docker running:

```sh
docker pull fkiecad/fact_extractor
wget https://raw.githubusercontent.com/fkie-cad/fact_extractor/master/extract.py
chmod +x extract.py
./extract.py ./relative/or/absolute/path/to/your/file
```

for more options see

```sh
./extract.py --help
```

## Local setup (aka not running through docker)

Install with:

```bash
fact_extractor/install/pre_install.sh
fact_extractor/install.py
```

:warning: **We no longer support Ubuntu 16.04 and Python <3.7** 
(It may still work with a bit of tinkering, though)

:warning: For the `generic_fs` unpacker plugin to work with all file system types, you may need to install extra kernel modules

```sh
sudo apt install linux-modules-extra-$(uname -r)
```

The tool can then be run with

```bash
fact_extractor/fact_extract.py [OPTIONS] PATH_TO_FIRMWARE
```
The tool is build with docker in mind.
To that end it extracts all files into a directory specified in the config.
The same directory also contains the meta data report.
Directories are created during installation, if config is changed make sure to recreate the folder structure.
It looks like:

```text
<path_to_data_folder>
├── files
└── reports
```


## Use docker container directly

Build with

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

:warning: Note that the container is run in privileged mode and shares the /dev folder. Thus the container can possibly harm your system in every way.


## Contribute
The easiest way to contribute is writing your own plug-in.
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
