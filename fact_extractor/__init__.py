import os
import pathlib as pl

firmware_magic_path = pl.Path(__file__).parent.parent / "bin" / "firmware"

os.environ["MAGIC"] = f'/usr/lib/file/magic.mgc:{firmware_magic_path}'
