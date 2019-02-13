# FACT extractor

Wraps FACT unpack plugins into standalone utility.
Should be able to extract most of the common container formats.


## Command line usage

Install with:

```bash
fact_extractor/install/pre_install.sh
# reboot your system if docker was not previously installed
fact_extractor/install.py
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


## Docker usage

Build with

```bash
docker build -t fact_extractor .
```

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
docker run -v <path_to_shared_folder>:/tmp/extractor --rm fact_extractor
```


## Contribute
The easiest way to contribute is writing your own plug-in.
Our Developers Manual can be found [here](https://github.com/fkie-cad/FACT_core/wiki/).

## Acknowledgments
This project is partly financed by [German Federal Office for Information Security (BSI)](https://www.bsi.bund.de) and others.  

## License
```
    Firmware Analysis and Comparison Tool (FACT) extractor
    Copyright (C) 2015-2019  Fraunhofer FKIE

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
