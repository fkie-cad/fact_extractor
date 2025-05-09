from __future__ import annotations

import struct
from pathlib import Path
from shlex import split
from subprocess import run
from typing import Any

# The keys are contained in D-Link's GPL source code release:
# https://ftp.dlink.de/m/m30/driver_software/M30_sw_reva_GPLcode.tgz
KEYS = [
    5707923367771304411745671248750824483,
    10894768012899131130521331528209746922,
    15288470472677139256755126505334224030,
    15684094658947152035377838769275126418,
    23335966381541562228843555154678213320,
    35758204719490132865802828225969932626,
    55796085441578870022055305014635464587,
    84685534971924495230307491298195576783,
    90689169725694446679934847122252508772,
    102843231306613166263088836093462280018,
    104150607981510203795488864067011889082,
    114757631173473038012387062720537970978,
    122827319385106288319261870763442386535,
    139748439958689321791739304844787857700,
    142445184766562174893386805873110982494,
    144584013712249949868423821316106489165,
    148910172501895975018656107080000705398,
    171163140727944594178400326348027629941,
    197309500221805730578821584982689310215,
    199166782498148755978511943517036940823,
    213332639786412688663978928290181517222,
    219279812981330897991123144996530024828,
    234873100902644763633564688918487935311,
    239326175726430359828602855454127173216,
    239684162915704711762592424676538179735,
    263148888178757173487260489009313288379,
    263186577619268302297875910062482816281,
    294812653955972892952199434070462443755,
    297229843036572496660253963048857992878,
    300193495476040623797083950726943683614,
    305304365912192958248475831895023682267,
    321768078914319598156789820506269093873,
    321924067544580491371387083761753396737,
    332370943350405508160278293449199176550,
]


NAME = 'D-Link MH01'
MIME_PATTERNS = ['firmware/dlink-mh01']
VERSION = '0.1.0'


class DLinkMh01UnpackerError(Exception):
    pass


class Mh01Header:
    """
    A MH01 imager contains two files and the header has the following format:
    magic: char[4]
    file 2 offset: uint32
    file 2 size: uint32
    endianness magic: uint16
    unknown: uint16
    The header is followed by the two payload files (size and offset of file 1 are implied)
    """

    SIZE = 16
    ENDIANNESS_OFFSET = 0xC
    PAYLOAD_OFFSET = 0x4

    def __init__(self, fp, offset: int = 0):
        self.fp = fp
        self.offset = offset

        endian_fmt = self._get_endianness_format()
        fp.seek(offset + self.PAYLOAD_OFFSET)
        self.file_2_offset = offset + self.SIZE + struct.unpack(f'{endian_fmt}I', fp.read(4))[0]
        self.file_2_size = struct.unpack(f'{endian_fmt}I', fp.read(4))[0]
        self.file_1_offset = offset + self.SIZE
        self.file_1_size = self.file_2_offset - self.file_1_offset

    def _get_endianness_format(self) -> str:
        self.fp.seek(self.offset + self.ENDIANNESS_OFFSET)
        endianness_field = self.fp.read(2)
        if endianness_field == b'\x2b\x1a':
            return '<'
        if endianness_field == b'\x1a\x2b':
            return '>'
        raise DLinkMh01UnpackerError('Invalid endianness')

    def read_file_1(self) -> bytes:
        self.fp.seek(self.file_1_offset)
        return self.fp.read(self.file_1_size)

    def read_file_2(self) -> bytes:
        self.fp.seek(self.file_2_offset)
        return self.fp.read(self.file_2_size)


def magic_is_correct(path: Path) -> bool:
    with path.open('rb') as fp:
        magic = fp.read(4)
        return magic == b'MH01'


def unpack_function(file_path: str, tmp_dir: str) -> dict[str, Any]:
    """
    The firmware image has the following structure:
    <MH01 header 1> [<MH01 header 2> <IV payload> <encrypted payload>] <checksum>
    So it's actually two nested MH01 images
    After decryption, the file has the following structure (another MH01 image):
    <MH01 header> <FW data> <checksum>
    """
    workdir = Path(tmp_dir)
    output = ''
    with Path(file_path).open('rb') as fp:
        outer_header = Mh01Header(fp)
        (workdir / 'Sig2.bin').write_bytes(outer_header.read_file_2())
        output += 'Saved outer signature to Sig2.bin\n'

        inner_header = Mh01Header(fp, outer_header.file_1_offset)
        iv = inner_header.read_file_1().decode().rstrip('\n')
        output += f'read IV from header: {iv}\n'

        enc_fw_path = workdir / 'fw.enc'
        enc_fw_path.write_bytes(inner_header.read_file_2())

    # now we try all known keys and hope that one works
    inner_container = workdir / 'fw_and_sig.bin'
    for k in KEYS:
        cmd = f'openssl aes-128-cbc -d -md sha256 -in {enc_fw_path} -out {inner_container} -k {k:032x} -iv {iv}'
        proc = run(split(cmd), capture_output=True, text=True, check=False)
        if proc.returncode == 0 and magic_is_correct(inner_container):
            break
    else:
        enc_fw_path.unlink()
        if inner_container.is_file():
            inner_container.unlink()
            output += 'decryption unsuccessful\n'
        return {'output': output}
    enc_fw_path.unlink()
    output += 'decryption successful\n'

    assert inner_container.is_file(), 'decrypted firmware file not found'
    with inner_container.open('rb') as fp:
        header = Mh01Header(fp)
        (workdir / 'Sig1.bin').write_bytes(header.read_file_2())
        output += 'Saved inner signature to Sig1.bin\n'

        (workdir / 'fw.bin').write_bytes(header.read_file_1())
        output += 'Saved decrypted firmware to fw.bin\n'

    inner_container.unlink()
    return {'output': output}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
