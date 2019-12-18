#!/usr/bin/env bash

echo "------------------------------------"
echo " Install RAW Extractor Dependencys  "
echo "------------------------------------"

# ToDo: branch must be removed when FS-support merged to master in common_helper_extraction
sudo -EH pip3 install --upgrade git+https://github.com/fkie-cad/common_helper_extraction.git@FS-support
	
exit 0