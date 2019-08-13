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
        xtek = Path(file_path).read_text().splitlines()
        for l in xtek:
            _rec_len = int(l[1:3], 16)
            _type = int(l[3])
            _actual_crc = int(l[4:6], 16)
            _addr_size = int(l[6], 16)
            _addr = int(l[7:15], 16)

            expected_crc = sum(int(i, 16) for i in (l[1:4] + l[6:])) & 0xff

            if _type != 8:
                try:
                    decoded += binascii.unhexlify(l[15:])
                except binascii.Error as tek_error:
                    return {'output': 'Unknown error in xtek record decoding: {}'.format(str(tek_error))}

                if _actual_crc != expected_crc:
                    return {'output': 'CRC mismatch in xtek record: {}'.format(l)}

            Path(target_file).write_bytes(decoded)

    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}
    except ValueError as v_error:
        return {'output': 'Failed to slice xtek record: {}'.format(str(v_error))}

    return {'output': 'Successfully decoded xtek file'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
