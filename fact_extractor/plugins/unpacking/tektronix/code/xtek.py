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
    decoded = b''
    target_file = Path(tmp_dir, Path(file_path).name)
    try:
        for rec in Path(file_path).read_text().splitlines():
            # _rec_len = int(rec[1:3], 16)  # information not used by now

            _type = int(rec[3])
            if _type == 3:
                continue
            if _type == 8:
                return write_decoded(decoded, target_file)

            if verify_crc(rec):
                return {'output': 'CRC mismatch in xtek record: {}'.format(rec)}

            decoded, decode_err = decode_record(decoded, rec)
            if decode_err:
                return decode_err

    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}
    except ValueError as v_error:
        return {'output': 'Failed to slice xtek record: {}'.format(str(v_error))}


def write_decoded(decoded, target_file):
    Path(target_file).write_bytes(decoded)
    return {'output': 'Successfully decoded xtek file'}


def verify_crc(rec):
    _actual_crc = int(rec[4:6], 16)
    expected_crc = sum(int(i, 16) for i in rec[1:4] + rec[6:]) & 0xff
    if _actual_crc != expected_crc:
        return 1


def get_data_field(rec):
    _addr_size = int(rec[6], 16)
    # _addr = int(rec[7:7 + _addr_size], 16)  # information not used by now
    _data = rec[7 + _addr_size:]
    return _data


def decode_record(decoded, rec):
    try:
        decoded += binascii.unhexlify(get_data_field(rec))
        return decoded, None
    except binascii.Error as tek_error:
        return None, {'output': 'Unknown error in xtek record decoding: {}'.format(str(tek_error))}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
