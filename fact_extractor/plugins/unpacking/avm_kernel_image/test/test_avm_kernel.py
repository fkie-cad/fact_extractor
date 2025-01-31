from test.unit.unpacker.test_unpacker import TestUnpackerBase

from ..code.avm_kernel_image import FIND_SQUASHFS_TOOL_PATH, UNPACK_KERNEL_TOOL_PATH


class TestAvmKernelImage(TestUnpackerBase):
    def test_unpacker_selection_generic(self):
        self.check_unpacker_selection('linux/avm-kernel-image-v1', 'avm_kernel_image')
        self.check_unpacker_selection('linux/avm-kernel-image-v2', 'avm_kernel_image')


def test_tool_pathes_set_correctly():
    assert FIND_SQUASHFS_TOOL_PATH.exists()
    assert UNPACK_KERNEL_TOOL_PATH.exists()
    assert str(FIND_SQUASHFS_TOOL_PATH)[0] == '/'
