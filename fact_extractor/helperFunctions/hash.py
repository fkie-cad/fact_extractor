import hashlib
from hashlib import new

from helperFunctions.dataConversion import make_bytes

HASH_BUFFER_SIZE = 64 * 1024  # 64KB

def get_hash(hash_function, binary):
    binary = make_bytes(binary)
    raw_hash = new(hash_function)
    raw_hash.update(binary)
    string_hash = raw_hash.hexdigest()
    return string_hash


def get_sha256(code):
    return get_hash('sha256', code)


def compute_sha256_of_file(file_path):
    """ Computes the sha256 of the given file's contents """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(HASH_BUFFER_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()
