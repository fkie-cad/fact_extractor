#!/usr/bin/env python3

import argparse
import binascii
import hashlib
import pathlib
import sys
from contextlib import suppress

from Crypto.Cipher import AES

CIPHERTEXT_OFF = 0x6DC
SHA512_DEC_FW_W_KEY_OFF = 0x1C
SHA512_DEC_FW = 0x5C
SHA512_ENC_FW = 0x9C
IVEC_OFF = 0xC
DATA_LEN_DEC_FW_OFF = 0x4
DATALEN_DEC_FW_NO_PADDING_OFF = 0x8
IVEC_LEN = 0x10
DATA_LEN = 0x4


class DcryptLink:
    def __init__(self, enc_fw, dec_fw):
        self.enc_fw = enc_fw
        self.dec_fw = dec_fw
        self.dec_key = None
        self.data_len_dec_fw_no_padding = None
        self.data_len_dec_fw = None
        self.ivec = None
        self.__setup__()

    def __setup__(self):
        self.set_decryption_key()
        self.set_datalen_variables()
        self.set_ivec()

    @staticmethod
    def get_expected_sha512_from_fd_at_offset(file, offset, size=0x40):
        with open(file, 'rb') as enc_fw:
            enc_fw.seek(offset)
            return binascii.hexlify(enc_fw.read(size)).decode()

    @staticmethod
    def calc_sha512_from_fd_at_offset_of_len(file, offset_payload, len_payload, key=None):
        with open(file, 'rb') as enc_fw:
            enc_fw.seek(offset_payload)
            data = enc_fw.read(len_payload)
            if key:
                data = data + key
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def verify(calculated, expected):
        if expected != calculated:
            print('\t[!] Failed!')  # noqa: T201
            raise ValueError
        print('\t[+] OK!')  # noqa: T201
        return 0

    def decrypt_aes128_cbc(self):
        with open(self.enc_fw, 'rb') as enc_fw:
            enc_fw.seek(CIPHERTEXT_OFF)
            ciphertext = enc_fw.read(self.data_len_dec_fw_no_padding)
        cipher = AES.new(self.dec_key, AES.MODE_CBC, self.ivec)
        plaintext = cipher.decrypt(ciphertext)
        pathlib.Path(self.dec_fw).open('wb').write(plaintext)

    def verify_magic_bytes(self):
        expected = b'SHRS'
        actual = pathlib.Path(self.enc_fw).open('rb').read(4)
        print('[*] Checking magic bytes...')  # noqa: T201
        self.verify(actual, expected)

    def set_datalen_variables(self):
        with open(self.enc_fw, 'rb') as enc_fw:
            enc_fw.seek(DATA_LEN_DEC_FW_OFF)
            self.data_len_dec_fw = int.from_bytes(enc_fw.read(DATA_LEN), byteorder='big', signed=False)
            enc_fw.seek(DATALEN_DEC_FW_NO_PADDING_OFF)
            self.data_len_dec_fw_no_padding = int.from_bytes(enc_fw.read(DATA_LEN), byteorder='big', signed=False)

    def set_ivec(self):
        with open(self.enc_fw, 'rb') as enc_fw:
            enc_fw.seek(IVEC_OFF)
            self.ivec = enc_fw.read(IVEC_LEN)

    def set_decryption_key(self):
        print('[*] Calculating decryption key...')  # noqa: T201

        in_file = bytes.fromhex('C8D32F409CACB347C8D26FDCB9090B3C')
        user_key = bytes.fromhex('358790034519F8C8235DB6492839A73F')
        ivec = bytes.fromhex('98C9D8F0133D0695E2A709C8B69682D4')
        cipher = AES.new(user_key, AES.MODE_CBC, ivec)
        self.dec_key = cipher.decrypt(in_file)

        self.verify(self.dec_key, bytes.fromhex('C05FBF1936C99429CE2A0781F08D6AD8'))


def main():
    arg_parser = argparse.ArgumentParser(description='D-Link SHRS decyption tool')
    arg_parser.add_argument('-i', '--inp', type=str, help='Path to the encrypted D-Link firmware image', required=True)
    arg_parser.add_argument('-o', '--out', type=str, help='Path to the decrypted firmware image', required=True)
    cli_args = arg_parser.parse_args()

    dlink = DcryptLink(cli_args.inp, cli_args.out)

    try:
        dlink.verify_magic_bytes()

        print('[*] Verifying SHA512 message digest of encrypted payload...')  # noqa: T201
        md = dlink.calc_sha512_from_fd_at_offset_of_len(dlink.enc_fw, CIPHERTEXT_OFF, dlink.data_len_dec_fw_no_padding)
        expected_md = dlink.get_expected_sha512_from_fd_at_offset(dlink.enc_fw, SHA512_ENC_FW)
        dlink.verify(md, expected_md)

        dlink.decrypt_aes128_cbc()

        print('[*] Verifying SHA512 message digests of decrypted payload...')  # noqa: T201
        md = dlink.calc_sha512_from_fd_at_offset_of_len(dlink.dec_fw, 0, dlink.data_len_dec_fw)
        expected_md = dlink.get_expected_sha512_from_fd_at_offset(dlink.enc_fw, SHA512_DEC_FW)
        dlink.verify(md, expected_md)

        md = dlink.calc_sha512_from_fd_at_offset_of_len(dlink.dec_fw, 0, dlink.data_len_dec_fw, key=dlink.dec_key)
        expected_md = dlink.get_expected_sha512_from_fd_at_offset(dlink.enc_fw, SHA512_DEC_FW_W_KEY_OFF)
        dlink.verify(md, expected_md)

        print(f'[+] Successfully decrypted {pathlib.Path(dlink.enc_fw).name}!')  # noqa: T201
    except ValueError:
        with suppress(FileNotFoundError):
            pathlib.Path(dlink.dec_fw).unlink()
        print('[!] Failed!')  # noqa: T201
        sys.exit(1)


if __name__ == '__main__':
    main()
