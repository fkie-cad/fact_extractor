'''
This plugin decodes / unpacks Tektronix extended hex files (.xtek)
'''
import binascii
import string
from pathlib import Path

NAME = 'Tektronix extended HEX'
MIME_PATTERNS = ['firmware/xtek']
VERSION = '0.1'


class XtekUnpackerError(Exception):
    pass


def unpack_function(file_path, tmp_dir):
    '''
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    '''
    decoded = b''
    target_file = Path(tmp_dir, Path(file_path).name)
    try:

        for rec in Path(file_path).read_text().splitlines():
            decoded += decode_records(rec)
        return write_decoded(decoded, target_file)
    except binascii.Error as tek_error:
        return {'output': 'Unknown error in xtek record decoding: {}'.format(str(tek_error))}
    except ValueError as v_error:
        return {'output': 'Failed to slice xtek record: {}'.format(str(v_error))}
    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}
    except XtekUnpackerError as xtek_err:
        return {'output': str(xtek_err)}


def decode_records(rec):
    if not is_valid_character_set(rec):
        raise XtekUnpackerError('Invalid characters in record {}'.format(rec))

    _type = int(rec[3])
    if _type not in [3, 8]:
        if not is_valid_record_length(rec):
            raise XtekUnpackerError('Record length mismatch in xtek record: {}'.format(rec))

        if not is_valid_crc(rec):
            raise XtekUnpackerError('CRC mismatch in xtek record: {}'.format(rec))
    return decode_record(rec)


def is_valid_character_set(rec):
    return all(c in string.hexdigits + '.sec' for c in rec[1:])


def write_decoded(decoded, target_file):
    try:
        Path(target_file).write_bytes(decoded)
        return {'output': 'Successfully decoded xtek file'}
    except FileNotFoundError as fnf_error:
        return {'output': 'Failed to open file: {}'.format(str(fnf_error))}


def is_valid_record_length(rec):
    _rec_len = int(rec[1:3], 16)
    return _rec_len == len(rec) - 1


def is_valid_crc(rec):
    _actual_crc = int(rec[4:6], 16)
    expected_crc = sum(int(i, 16) for i in rec[1:4] + rec[6:]) & 0xff
    return _actual_crc == expected_crc


def get_data_field(rec):
    _addr_size = int(rec[6], 16)
    # _addr = int(rec[7:7 + _addr_size], 16)  # information not used by now
    _data = rec[7 + _addr_size:]
    return _data


def decode_record(rec):
    return binascii.unhexlify(get_data_field(rec))


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
