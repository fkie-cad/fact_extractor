from pathlib import Path

from helperFunctions.config import load_config
from helperFunctions.file_system import get_test_data_dir


def test_load_config(monkeypatch):
    monkeypatch.setattr('helperFunctions.config.get_config_dir', lambda: Path(f'{get_test_data_dir()}/helperFunctions'))
    test_config = load_config('test.cfg')
    assert test_config.unpack.exclude == ["foobar"]
    assert test_config.expert_settings.statistics is False
