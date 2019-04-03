import pytest

from extract import container_exists, parse_arguments


def exec_stub(command, *_, **__):
    class ProcessResult:
        def __init__(self, rc):
            self.returncode = rc

    if command.endswith('fail'):
        return ProcessResult(255)
    return ProcessResult(0)


def test_parse_arguments(monkeypatch):
    monkeypatch.setattr('extract.sys.argv', ['extract.py', 'ANY'])
    args = parse_arguments()
    assert args.ARCHIVE[0] == 'ANY'


def test_parse_arguments_missing_archive(monkeypatch, capsys):
    monkeypatch.setattr('extract.sys.argv', ['extract.py'])

    with pytest.raises(SystemExit) as sys_exit:
        parse_arguments()
    assert 'required: ARCHIVE' in capsys.readouterr().err
    assert sys_exit.value.code == 2


def test_parse_arguments_show_version(monkeypatch, capsys):
    monkeypatch.setattr('extract.sys.argv', ['extract.py', '--version'])

    with pytest.raises(SystemExit) as sys_exit:
        parse_arguments()
    assert '0.1' in capsys.readouterr().out
    assert sys_exit.value.code == 0


def test_container_exists(monkeypatch):
    monkeypatch.setattr('extract.subprocess.run', exec_stub)

    assert not container_exists('please fail')
    assert container_exists('please succeed')
