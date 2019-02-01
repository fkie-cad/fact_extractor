from hashlib import new

from helperFunctions.dataConversion import make_bytes


def get_hash(hash_function, binary):
    binary = make_bytes(binary)
    raw_hash = new(hash_function)
    raw_hash.update(binary)
    string_hash = raw_hash.hexdigest()
    return string_hash


def get_sha256(code):
    return get_hash('sha256', code)

