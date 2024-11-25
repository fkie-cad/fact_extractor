import binascii
import json
import types


class ReportEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            try:
                return o.decode(encoding='utf-8')
            except UnicodeDecodeError:
                return binascii.b2a_hex(o)
        if isinstance(o, (types.GeneratorType, tuple, set)):
            return str(list(o))

        return json.JSONEncoder.default(self, o)


def make_bytes(code):
    if isinstance(code, bytes):
        return code
    if isinstance(code, str):
        return code.encode('utf-8')
    return bytes(code)


def make_unicode_string(code):
    if isinstance(code, str):
        return code.encode(errors='replace').decode()
    if isinstance(code, bytes):
        return code.decode(errors='replace')
    return code.__str__()


def remove_uneccessary_spaces(input_string):
    tmp = input_string.split()
    return ' '.join(tmp)
