'''
This plugin decodes / unpacks Tektronix extended hex files (.xtek)
'''
import binascii
from pathlib import Path

NAME = 'Tektronix extended HEX'
MIME_PATTERNS = ['firmware/xtek']
VERSION = '0.1'


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    target_file = Path(tmp_dir, Path(file_path).name)
    decoded = b''
    try:
        for rec in Path(file_path).read_text().splitlines():
            _rec_len = int(rec[1:3], 16)

            _type = int(rec[3])
            if _type == 3:
                continue
            if _type == 8:
                Path(target_file).write_bytes(decoded)
                return {'output': 'Successfully decoded xtek file'}

            _actual_crc = int(rec[4:6], 16)
            _addr_size = int(rec[6], 16)
            _addr = int(rec[7:7 + _addr_size], 16)
            _data = rec[7 + _addr_size:]

            expected_crc = sum(int(i, 16) for i in rec[1:4] + rec[6:]) & 0xff

            if _actual_crc != expected_crc:
                return {'output': 'CRC mismatch in xtek record: {}'.format(rec)}

            try:
                decoded += binascii.unhexlify(_data)
            except binascii.Error as tek_error:
                return {'output': 'Unknown error in xtek record decoding: {}'.format(str(tek_error))}

    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}
    except ValueError as v_error:
        return {'output': 'Failed to slice xtek record: {}'.format(str(v_error))}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
