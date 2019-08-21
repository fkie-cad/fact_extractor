'''
This plugin decodes / unpacks Tektronix extended hex files (.xtek)
'''
import binascii
import string
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
    read_records = get_records(file_path)
    if isinstance(read_records, dict):
        return read_records

    for rec in Path(file_path).read_text().splitlines():
        _dec = decode_records(rec)
        if not isinstance(_dec, dict):
            decoded += _dec
        else:
            return _dec
    return write_decoded(decoded, target_file)


def decode_records(rec):
    if verify_alphabet(rec):
        return {'output': 'Invalid characters in record: {}'.format(rec)}

    _type = int(rec[3])
    if _type not in [3, 8]:
        vrec_len = verify_rec_len(rec)
        if vrec_len:
            return vrec_len

        if verify_crc(rec):
            return {'output': 'CRC mismatch in xtek record: {}'.format(rec)}

    return decode_record(rec)


def get_records(_file):
    try:
        return Path(_file).read_text().splitlines()
    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}


def verify_alphabet(rec):
    if all(c in string.hexdigits + '.sec' for c in rec[1:]):
        return None
    return 1


def write_decoded(decoded, target_file):
    try:
        Path(target_file).write_bytes(decoded)
        return {'output': 'Successfully decoded xtek file'}
    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}


def verify_rec_len(rec):
    try:
        _rec_len = int(rec[1:3], 16)
        if _rec_len != len(rec) - 1:
            return {'output': 'Record length mismatch in xtek record: {}'.format(rec)}
        return None
    except ValueError as v_error:
        return {'output': 'Failed to slice xtek record: {}'.format(str(v_error))}


def verify_crc(rec):
    _actual_crc = int(rec[4:6], 16)
    expected_crc = sum(int(i, 16) for i in rec[1:4] + rec[6:]) & 0xff
    if _actual_crc != expected_crc:
        return 1
    return None


def get_data_field(rec):
    _addr_size = int(rec[6], 16)
    # _addr = int(rec[7:7 + _addr_size], 16)  # information not used by now
    _data = rec[7 + _addr_size:]
    return _data


def decode_record(rec):
    try:
        return binascii.unhexlify(get_data_field(rec))
    except binascii.Error as tek_error:
        return {'output': 'Unknown error in xtek record decoding: {}'.format(str(tek_error))}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
