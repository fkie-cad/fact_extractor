import binascii
import logging
import os
import re
from base64 import a85decode

from common_helper_files import get_binary_from_file, write_binary_to_file

from helperFunctions.dataConversion import make_bytes, make_unicode_string, remove_uneccessary_spaces

NAME = 'Postscript'
MIME_PATTERNS = ['text/postscript']
VERSION = '0.4'

ENCODING_OVERHEAD = 0.25

META_FIELDS = ['Title', 'For', 'Product', 'Release', 'Release ?Date', 'Release ?Versions', 'TargetDevice']
FILE_HEADER = re.compile(b'currentfile /ASCII85Decode( filter [/\\w]+)*( exec)?\\s')
FILE_FOOTER = re.compile(b'~>')


def unpack_function(file_path, tmp_dir):
    raw = get_binary_from_file(file_path)
    meta_dict = _get_meta_data(raw)
    meta_dict['encoding_overhead'] = ENCODING_OVERHEAD
    payloads = _get_payloads(raw)
    _store_files(payloads, tmp_dir)
    return meta_dict


def _get_meta_data(raw):
    meta = {}
    for item in META_FIELDS:
        tmp = re.search(b'%%%? ?(' + make_bytes(item) + b'):([\\w=., -]+)', raw)
        if tmp:
            meta[make_unicode_string(tmp.group(1))] = remove_uneccessary_spaces(make_unicode_string(tmp.group(2)))
    return meta


def _get_payloads(raw):
    raw_payloads = _get_raw_payloads(raw)
    return _convert_payloads(raw_payloads)


def _convert_payloads(raw_payloads):
    payloads = []
    for item in raw_payloads:
        try:
            payloads.append(a85decode(item, adobe=True))
        except binascii.Error as error_message:
            logging.error(f'Could not decode payload: {error_message}')
    return payloads


def _get_raw_payloads(raw):
    raw_payloads = []
    pos = 0
    while pos < len(raw):
        current_payload, end_pos = _get_next_payload(raw, pos)
        if current_payload is not None:
            raw_payloads.append(current_payload)
            pos = end_pos
        else:
            break
    return raw_payloads


def _get_next_payload(raw, start_pos, payload_header_regex=FILE_HEADER, payload_footer_regex=FILE_FOOTER):
    payload_header = payload_header_regex.search(raw, start_pos)
    if payload_header:
        payload_footer = payload_footer_regex.search(raw, payload_header.end())
        if payload_footer:
            return raw[payload_header.end() : payload_footer.end()], payload_footer.end()
        logging.error('End of Payload could not be found!')
        return None, len(raw)
    return None, len(raw)


def _store_files(payloads, tmp_dir):
    counter = 0
    for item in payloads:
        write_binary_to_file(item, os.path.join(tmp_dir, f'payload_{counter}.bin'))
        counter += 1


# ----> Do not edit below this line <----


def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
