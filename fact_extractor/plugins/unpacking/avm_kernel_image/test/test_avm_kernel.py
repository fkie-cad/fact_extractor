from test.unit.unpacker.test_unpacker import TestUnpackerBase
from ..code.avm_kernel_image import _fix_lzma_header, FIXED_LZMA_HEADER


TEST_AVM_LZMA_STREAM = b'\x5d\x00\x00\x80\x00\x00\x00\x00Some_data'


class TestAvmKernelImage(TestUnpackerBase):

    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('linux/avm-kernel-image-v1', 'avm_kernel_image')
        self.check_unpacker_selection('linux/avm-kernel-image-v2', 'avm_kernel_image')


def test_fix_lzma_header():
    fixed_stream = _fix_lzma_header(TEST_AVM_LZMA_STREAM)
    assert isinstance(fixed_stream, bytes)
    assert fixed_stream == FIXED_LZMA_HEADER + b'Some_data'
