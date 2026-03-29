'''
This plugin unpacks draytek update files.
'''

# This file essentially is a refactor of
#https://github.com/infobyte/draytek-arsenal/blob/d601252b2e6a62e3cd3e5962e164d32dabf1c6ae/draytek_arsenal/src/draytek_arsenal/commands/parse.py
#https://github.com/infobyte/draytek-arsenal/blob/d601252b2e6a62e3cd3e5962e164d32dabf1c6ae/draytek_arsenal/src/draytek_arsenal/commands/extract.py

# The original code comes with the following license:
'''
MIT License

Copyright (c) 2024 Faraday

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

# The refactored code however, is licensed under the GNU GPL 3 License
from pathlib import Path
import tempfile
from struct import pack

from draytek_arsenal.format import parse_firmware
from draytek_arsenal.draytek_format import Draytek
from draytek_arsenal.linux import DraytekLinux

from draytek_arsenal.compression import Lz4 as CustomLz4
from draytek_arsenal.fs import PFSExtractor

NAME = 'draytek_arsenal'
MIME_PATTERNS = ['firmware/draytek-rtos']
VERSION = '0.0'


def unpack_function(file_path: str, tmp_dir: str) -> dict:
    '''
    file_path specifies the input file.
    tmp_dir must be used to store the extracted files.
    Optional: Return a dict with meta information
    '''
    output_dir = Path(tmp_dir)
    structured_firmware = parse_firmware(file_path)

    if not isinstance(structured_firmware, Draytek):
        raise Exception("The given image could not be parsed as Draytek-RTOS")

    META_DICT = structure_rtos_metadata(structured_firmware)

    unpacking_errors: str = unpack_rtos_firmware(structured_firmware, output_dir)

    if unpacking_errors != '':
        META_DICT["ocurred_errors_while_unpacking"] = unpacking_errors

    return META_DICT

def structure_rtos_metadata(structured_firmware: Draytek) -> dict:
    return {
        "type": "RTOS",
        "bin": {
            "header": {
                "size": hex(structured_firmware.bin.header.size),
                "version_info": hex(structured_firmware.bin.header.version_info),
                "next_section": hex(structured_firmware.bin.header.next_section.value),
                "adjusted_size": hex(structured_firmware.bin.header.adj_size),
                "bootloader_version": structured_firmware.bin.header.bootloader_version,
                "product_number": structured_firmware.bin.header.product_number
            },
            "rtos": {
                "size": hex(structured_firmware.bin.rtos.rtos_size)
            },
            "checksum": hex(structured_firmware.bin.checksum)

        },
        "web": {
            "header": {
                "size": hex(structured_firmware.web.header.size),
                "adjusted_size": hex(structured_firmware.web.header.adj_size),
                "next_section": hex(structured_firmware.web.header.next_section)
            },
            "checksum": hex(structured_firmware.web.checksum)
        }
    }

def unpack_rtos_firmware(structured_firmware: Draytek, output_dir: Path) -> str:
    errors_while_unpacking = ''

    # Unpack bootloader and rtos
    if structured_firmware.bin.rtos.rtos_size != len(structured_firmware.bin.rtos.data):
        errors_while_unpacking += f'Data length ({len(structured_firmware.bin.rtos.data)}) doesn\'t match with the header length ({structured_firmware.bin.rtos.rtos_size})\n'
    else:
        write_bootloader_and_rtos(structured_firmware, output_dir / 'bootloader_and_rtos')

    # Write Dynamic Kernel Modules
    if structured_firmware.has_dlm:
        write_encrypted_dynamic_kernel_modules(structured_firmware, output_dir / 'dlms')
    else:
        errors_while_unpacking += 'File has no dynamic kernel images\n'

    # Unpack web directory
    web_output_dir = output_dir / 'web'
    web_output_dir.mkdir()
    write_web_filesystem(structured_firmware, web_output_dir)

    return errors_while_unpacking

def write_bootloader_and_rtos(structured_firmware: Draytek, output_file: Path) -> None:
    unstructured_bootloader = b"".join([pack(">I", integer) for integer in structured_firmware.bin.bootloader.data[:-1]])

    lz4 = CustomLz4()
    decompressed_rtos = lz4.decompress(structured_firmware.bin.rtos.data)

    output_file.write_bytes(unstructured_bootloader + decompressed_rtos)

def write_web_filesystem(structured_firmware: Draytek, web_output_dir: Path) -> None:
    with tempfile.NamedTemporaryFile() as tmp_dir_for_lz4_decompression:
        lz4 = CustomLz4()
        tmp_dir_for_lz4_decompression.write(
            lz4.decompress(structured_firmware.web.data)
        )

        pfs_extractor = PFSExtractor()
        _ = pfs_extractor.extract(tmp_dir_for_lz4_decompression.name, str(web_output_dir))

def write_encrypted_dynamic_kernel_modules(structured_firmware: Draytek, output_file: Path) -> None:
    data = b"DLM/1.0" + structured_firmware.bin.dlm.data
    output_file.write_bytes(data)

# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
