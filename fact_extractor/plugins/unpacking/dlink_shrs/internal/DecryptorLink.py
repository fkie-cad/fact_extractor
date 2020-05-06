#!/usr/bin/env python3

import hashlib
import sys
import binascii
import pathlib

from Crypto.Cipher import AES


class DcryptLink:

    def __init__(self):
        self.enc_fw = sys.argv[1]
        self.dec_fw = sys.argv[2]
        self.dec_key = None
        self.dataLen1 = None
        self.dataLen2 = None
        self.ivec = None
        self.__setup__()

    def __setup__(self):
        self.set_decryption_key()
        self.set_datalen_variables()
        self.set_ivec()

    @staticmethod
    def get_expected_sha512_from_fd_at_offset(file, offset, size=0x40):
        with open(file, 'rb') as f:
            f.seek(offset, 0)
            return binascii.hexlify(f.read(size)).decode()

    @staticmethod
    def calc_sha512_from_fd_at_offset_of_len(file, offset_payload, len_payload, key=None):
        with open(file, 'rb') as f:
            f.seek(offset_payload, 0)
            data = f.read(len_payload)
            if key:
                data = data + key
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def verify(calculated, expected):
        assert expected == calculated, f"\nExpected:\n  {expected}\nGot:\n  {calculated}"
        print("\t[+] OK!")
        return 1

    def decrypt_aes128_cbc(self):
        with open(self.enc_fw, 'rb') as f:
            f.seek(0x6dc)
            ciphertext = f.read(self.dataLen1)
        cipher = AES.new(self.dec_key, AES.MODE_CBC, self.ivec)
        plaintext = cipher.decrypt(ciphertext)
        with open(self.dec_fw, 'wb') as f:
            f.write(plaintext)

    def verify_magic_bytes(self):
        expected = "SHRS"
        with open(self.enc_fw, 'rb') as f:
            calculated_magic = f.read(4).decode()
        print("[*] Checking magic bytes...")
        return self.verify(calculated_magic, expected)

    def set_datalen_variables(self):
        with open(self.enc_fw, 'rb') as f:
            f.seek(0x4, 0)
            self.dataLen2 = int.from_bytes(f.read(4), byteorder='big', signed=False)
            f.seek(0x8, 0)
            self.dataLen1 = int.from_bytes(f.read(4), byteorder='big', signed=False)

    def set_ivec(self):
        with open(self.enc_fw, 'rb') as f:
            f.seek(0xc, 0)
            self.ivec = f.read(16)

    def set_decryption_key(self):
        print("[*] Calculating decryption key...")

        inFile = bytes.fromhex('C8D32F409CACB347C8D26FDCB9090B3C')
        userKey = bytes.fromhex('358790034519F8C8235DB6492839A73F')
        ivec = bytes.fromhex('98C9D8F0133D0695E2A709C8B69682D4')
        cipher = AES.new(userKey, AES.MODE_CBC, ivec)
        self.dec_key = cipher.decrypt(inFile)

        self.verify(self.dec_key, bytes.fromhex('C05FBF1936C99429CE2A0781F08D6AD8'))


def main():
    if (len(sys.argv) != 3):
        print(f"Usage: python3 {sys.argv[0]} <encrypted binary> <decrypted file>")
        exit(-1)

    dlink = DcryptLink()

    if dlink.verify_magic_bytes():
        print("[*] Verifying SHA512 message digest of encrypted payload...")

        md = dlink.calc_sha512_from_fd_at_offset_of_len(dlink.enc_fw, 0x6dc, dlink.dataLen1)
        expected_md = dlink.get_expected_sha512_from_fd_at_offset(dlink.enc_fw, 0x9c)

        if dlink.verify(md, expected_md):
            print("[*] Verifying SHA512 message digests of decrypted payload...")

            dlink.decrypt_aes128_cbc()

            md = dlink.calc_sha512_from_fd_at_offset_of_len(dlink.dec_fw, 0, dlink.dataLen2)
            expected_md = dlink.get_expected_sha512_from_fd_at_offset(dlink.enc_fw, 0x5c)

            if dlink.verify(md, expected_md):

                md = dlink.calc_sha512_from_fd_at_offset_of_len(dlink.dec_fw, 0, dlink.dataLen2, key=dlink.dec_key)
                expected_md = dlink.get_expected_sha512_from_fd_at_offset(dlink.enc_fw, 0x1c)
                if dlink.verify(md, expected_md):
                    print(f"[+] Successfully decrypted {dlink.enc_fw.split('/')[-1]}!")
                else:
                    pathlib.Path(dlink.dec_fw).unlink()


if __name__ == '__main__':
    main()
