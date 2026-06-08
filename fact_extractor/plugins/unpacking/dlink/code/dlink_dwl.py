from __future__ import annotations

import hmac
import re
from hashlib import md5, sha1
from pathlib import Path
from typing import Any, Literal

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Decryption of D-Link DWL FW images using the data from the header
# reference: https://openwrt.org/toh/d-link/d-link_dwl_series_of_business_access_points

NAME = 'D-Link DWL'
MIME_PATTERNS = ['firmware/dlink-dwl']
VERSION = '0.1.0'
HEADER_SIZE = 0x74
MODEL_HEADER_OFFSET = 0x4
HMAC_HEADER_OFFSET = 0x24


def unpack_function(file_path: str, tmp_dir: str) -> dict[str, Any]:
    path = Path(file_path)
    with path.open(mode='rb') as fp:
        header = fp.read(HEADER_SIZE)
        cypher = fp.read()

    msg = _get_null_terminated_str(header, MODEL_HEADER_OFFSET)
    key = _get_null_terminated_str(header, HMAC_HEADER_OFFSET)
    decryption_key = hmac.new(key, msg, sha1).hexdigest()

    try:
        model_number = re.findall(rb'\d{4}', msg)[0].decode()
        mode = AES.MODE_ECB if model_number.startswith('8') else AES.MODE_CBC
        plaintext = decrypt_openssl_aes(cypher, decryption_key.encode(), mode=mode)
        output_file = Path(tmp_dir) / f'{msg.decode()}.decrypted'
        output_file.write_bytes(plaintext)
    except IndexError:
        return {'output': 'Error during decryption: Could not find model number'}
    except Exception as e:
        return {'output': f'Error during decryption: {e}'}
    mode_str = 'ecb' if mode == AES.MODE_ECB else 'cbc'
    return {'output': f'Successfully decrypted file with aes-256-{mode_str} using key {decryption_key}'}


def _get_null_terminated_str(data: bytes, start_offset: int) -> bytes:
    return data[start_offset : data.find(b'\x00', start_offset)]


def _convert_evp_to_key_and_iv(password: bytes, salt: bytes, key_len: int = 32, iv_len: int = 16):
    # converts OpelSSL EnVelope (EVP) string to AES key and IV values
    digest, generated = None, b''
    while len(generated) < (key_len + iv_len):
        digest = md5((digest or b'') + password + salt).digest()
        generated += digest
    key = generated[:key_len]
    iv = generated[key_len : key_len + iv_len]
    return key, iv


def decrypt_openssl_aes(data: bytes, password: bytes, mode: Literal[AES.MODE_ECB, AES.MODE_CBC]) -> bytes:
    assert data[:8] == b'Salted__', 'Error: Data is not in OpenSSL format'
    salt = data[8:16]
    ciphertext = data[16:]

    if mode == AES.MODE_CBC:
        key, iv = _convert_evp_to_key_and_iv(password, salt)
        cipher = AES.new(key, mode, iv)
    elif mode == AES.MODE_ECB:
        key, _ = _convert_evp_to_key_and_iv(password, salt, iv_len=0)
        cipher = AES.new(key, mode)
    else:
        raise ValueError(f'Invalid mode {mode}')
    padded_plaintext = cipher.decrypt(ciphertext)

    try:
        return unpad(padded_plaintext, AES.block_size)
    except ValueError:
        return padded_plaintext


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
