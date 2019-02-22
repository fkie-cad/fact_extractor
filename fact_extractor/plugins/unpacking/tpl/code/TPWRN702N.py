import binascii
from struct import unpack

from common_helper_files import write_binary_to_file
from unpacker.helper.carving import Carver

NAME = 'TP-WR702N'
MIME_PATTERNS = ['firmware/tp-wr702n']
VERSION = '0.1.1'


class InvalidImg0InformationException(Exception):
    pass


class Img0MissingException(Exception):
    pass


class NotLZMAException(Exception):
    pass


def unpack_function(file_path, tmp_dir):
    """
    file_path specifies the input file.
    tmp_dir should be used to store the extracted files.
    """
    tpwr702n = TPWR702N(file_path)

    write_binary_to_file(tpwr702n.get_container_header(), '{}/container_header.hdr'.format(tmp_dir))
    write_binary_to_file(tpwr702n.get_tpimg0_header(), '{}/img0.hdr'.format(tmp_dir))
    write_binary_to_file(tpwr702n.get_bootloader(), '{}/bootloader.7z'.format(tmp_dir))
    write_binary_to_file(tpwr702n.get_os_and_fs(), '{}/main.img'.format(tmp_dir))
    write_binary_to_file(tpwr702n.get_os(), '{}/main.7z'.format(tmp_dir))
    write_binary_to_file(tpwr702n.get_fs(), '{}/main.owfs'.format(tmp_dir))

    remaining = tpwr702n.get_remaining_blocks()
    for offset in remaining:
        write_binary_to_file(remaining[offset], '{}/{}_unknown.bin'.format(tmp_dir, offset))

    return tpwr702n.get_meta_dict()


class TPWR702N:
    MD5SIZE = 16

    # -------- Devices --------
    IMG0_OFFSET = 20
    IMG0_HEADER_SIZE = 12
    BOOTLOADER_OFFSET = 26820
    OS_OFFSET = 262420

    def __init__(self, filename):
        self.img0 = None
        self.md5_checksum = None
        self.firmware_filepath = filename
        self.firmware = open(filename, 'rb')
        self._read_container_information()
        self.firmware.close()

        self.carver = Carver(self.firmware_filepath)

    def __str__(self):
        return 'MD5: {} \n Included Header:\n{}'.format(self.get_md5string(), str(self.img0))

    def get_remaining_blocks(self):
        non_carved_areas = self.carver.carved.non_carved_areas

        remaining = {}
        for area in non_carved_areas:
            remaining[area[0]] = self.carver.extract_data(area[0], area[1])
        return remaining

    def get_container_header(self):
        return self.carver.extract_data(0, 19)

    def get_md5string(self):
        return binascii.hexlify(self.md5_checksum).decode('ascii')

    def get_meta_dict(self):
        meta_data = {}
        meta_data['bootloader_offset'] = self.BOOTLOADER_OFFSET
        meta_data['os_offset'] = self.OS_OFFSET
        meta_data['md5'] = self.get_md5string()
        meta_data['img0'] = self.img0.get_meta_dict()
        meta_data['uncarved_area'] = self.carver.carved.non_carved_areas
        return meta_data

    def _read_container_information(self):
        header = unpack('>4s16s', self.firmware.read(4 + self.MD5SIZE))
        self.container_format = header[0]
        self.md5_checksum = header[1]

        self._read_img0()

    def _read_img0(self):
        self.img0 = TPIMG0(self.firmware_filepath, self.IMG0_OFFSET)

    def get_tpimg0_header(self):
        return self.carver.extract_data(self.IMG0_OFFSET, self.IMG0_OFFSET + self.IMG0_HEADER_SIZE)

    def get_bootloader(self):
        bootloader_size = self._get_end_of_bootloader() - self.BOOTLOADER_OFFSET
        bootloader = self.carver.extract_data(self.BOOTLOADER_OFFSET, self.BOOTLOADER_OFFSET + bootloader_size)
        self._check_expected_lzma_property(bootloader)
        return bootloader

    def _get_end_of_bootloader(self):
        if self.img0 is None:
            raise Img0MissingException('Main IMG0 is missing')
        if self.img0.sub_header is None:
            raise Img0MissingException('Sub IMG0 is missing')

        return self.img0.sub_header.offset - 1

    @staticmethod
    def _check_expected_lzma_property(data_block):
        lzma_first_byte = b'\x6e'
        if data_block[0] is not lzma_first_byte[0]:
            raise NotLZMAException

    def get_os_and_fs(self):
        os_and_fs = self.carver.extract_data(self.OS_OFFSET)
        self._check_expected_lzma_property(os_and_fs)
        return os_and_fs

    def get_os(self):
        os_and_fs = self.get_os_and_fs()
        end = self._find_fs_magic_string(os_and_fs)
        return os_and_fs[:end]

    def get_fs(self):
        os_and_fs = self.get_os_and_fs()
        end = self._find_fs_magic_string(os_and_fs)
        return os_and_fs[end:]

    @staticmethod
    def _find_fs_magic_string(os_and_fs):
        search_pattern = b'owowowowowowowowowowowowowowowow'
        return os_and_fs.find(search_pattern)


class TPIMG0:  # pylint: disable=too-many-instance-attributes
    # -------- TP-Link Languages --------
    LANGUAGE_TP_LINK_CHINESE = b'\x00\x01'
    LANGUAGE_TP_LINK_ENGLISH = b'\x11\x01'

    def __init__(self, filename, offset):
        self.offset = offset
        self.header_size = 12

        self.device_id = None
        self.language = None
        self.container_size = -1

        self.firmware_filepath = filename
        self.firmware = open(filename, 'rb')
        self.firmware.seek(offset)
        self._read_container_information()
        self.sub_header = self._read_sub_header()
        self.firmware.close()

        self.check_header()

    def __str__(self):
        return 'IMG0\nSize: {}\nDevice ID: {}\nLanguage: {}\nSubheader: {}'.format(self.container_size, self.device_id, self.language, self.sub_header)

    def get_meta_dict(self):
        meta_data = {}
        meta_data['size'] = self.container_size
        meta_data['device_id'] = '0x{}'.format(binascii.hexlify(self.device_id).decode('ascii'))
        meta_data['language_code'] = '0x{}'.format(binascii.hexlify(self.language).decode('ascii'))
        meta_data['language'] = self.get_language_string()
        if self.sub_header is not None:
            meta_data['sub_header'] = self.sub_header.get_meta_dict()

        return meta_data

    def get_language_string(self):
        if self.language == self.LANGUAGE_TP_LINK_CHINESE:
            return 'Chinese'
        if self.language == self.LANGUAGE_TP_LINK_ENGLISH:
            return 'English'
        return 'Unknown'

    def _read_container_information(self):
        header = unpack('>4sI2s2s', self.firmware.read(self.header_size))
        self.container_size = header[1]
        self.device_id = header[2]
        self.language = header[3]

    def _read_sub_header(self):
        self.firmware.seek(self.offset + self.header_size)
        rest_of_the_file = self.firmware.read()
        sub_header_offset = rest_of_the_file.find(b'\x49\x4d\x47\x30')
        if sub_header_offset < 0:
            return None
        sub_header_offset = sub_header_offset + self.header_size + self.offset
        return TPIMG0(self.firmware_filepath, sub_header_offset)

    def check_header(self):
        if self.container_size <= 0:
            raise InvalidImg0InformationException('Size is {}'.format(self.container_size))

        if self.device_id is None:
            raise InvalidImg0InformationException('Device Id is missing')

        if self.language is None:
            raise InvalidImg0InformationException('Language is missing')

        return True

# ----> Do not edit below this line <----


def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
