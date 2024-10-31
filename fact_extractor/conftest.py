import pytest

from helperFunctions.program_setup import init_magic


@pytest.fixture(autouse=True)
def _init_magic():
    init_magic()
