import logging
from pathlib import Path

import pytest

from extract import (
    TemporaryDirectory,
    call_docker,
    container_exists,
    handle_report,
    main,
    parse_arguments,
    setup_logging,
)


def exec_stub(command, *_, **__):
    class ProcessResult:
        def __init__(self, rc):
            self.returncode = rc

        @property
        def stdout(self):
            return b''

    if command.endswith('fail'):
        return ProcessResult(255)
    return ProcessResult(0)


def test_parse_arguments(monkeypatch):
    monkeypatch.setattr('extract.sys.argv', ['extract.py', 'ANY'])
    args = parse_arguments()
    assert args.FILE[0] == 'ANY'


def test_parse_arguments_no_archive(monkeypatch, capsys):
    monkeypatch.setattr('extract.sys.argv', ['extract.py'])

    with pytest.raises(SystemExit) as sys_exit:
        parse_arguments()
    assert 'required: FILE' in capsys.readouterr().err
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


def test_setup_logging(capsys):
    logging.info('test')
    assert not capsys.readouterr().err

    setup_logging(verbose=False)
    logging.info('test')
    assert capsys.readouterr().err


def test_setup_logging_verbose(capsys):
    setup_logging(verbose=False)
    logging.debug('test')
    assert not capsys.readouterr().err

    setup_logging(verbose=True)
    logging.debug('test')
    assert capsys.readouterr().err


def test_handle_report(monkeypatch, capsys, tmpdir):
    monkeypatch.setattr('extract.Path.read_text', lambda *_, **__: '{"a": 5}')
    handle_report(None, '')
    assert '    "a": 5\n' in capsys.readouterr().out

    handle_report(str(Path(str(tmpdir), 'anyfile')), '')
    report = Path(str(tmpdir), 'anyfile').read_bytes().decode()
    assert '    "a": 5\n' in report


@pytest.mark.parametrize(
    ('arguments', 'return_code', 'message'),
    [
        (['extract.py', '-o', '/tmp', 'anyfile'], 1, 'Target directory exists'),
        (['extract.py', '-o', '/tmp/valid_dir', '-c', 'container_will_fail', 'anyfile'], 1, "fail doesn't exist"),
        (['extract.py', '-o', '/tmp/valid_dir', '-c', 'container_will_succeed', 'anyfile'], 1, "anyfile doesn't exist"),
        (
            [
                'extract.py',
                '-o',
                '/tmp/valid_dir',
                '-c',
                'container_will_succeed',
                '-r',
                '/tmp/bad/path/to/report',
                '/bin/bash',
            ],
            1,
            'Check if parent directory exists',
        ),
        (
            [
                'extract.py',
                '-o',
                '/tmp/valid_dir',
                '-c',
                'container_will_succeed',
                '-r',
                '/etc/environment',
                '/bin/bash',
            ],
            0,
            'will be overwritten',
        ),
        (
            ['extract.py', '-o', '/tmp/valid_dir', '-c', 'container_will_succeed', '-r', '/tmp/report', '/bin/bash'],
            0,
            '',
        ),
    ],
)
def test_main_return_values(arguments, return_code, message, monkeypatch, capsys):
    monkeypatch.setattr('extract.call_docker', lambda **_: None)
    monkeypatch.setattr('extract.sys.argv', arguments)
    monkeypatch.setattr('extract.subprocess.run', exec_stub)

    assert main() == return_code
    assert message in capsys.readouterr().err


def test_call_docker(monkeypatch, capsys):
    monkeypatch.setattr('extract.subprocess.run', lambda *_, **__: None)
    tmpdir = TemporaryDirectory()
    target = Path(tmpdir.name, 'target')
    Path(tmpdir.name, 'reports').mkdir(parents=True)
    Path(tmpdir.name, 'reports', 'meta.json').write_text('{"test": "succeeded"}')

    call_docker('/bin/bash', 'doesnt_matter', str(target), None, '128', tmpdir)

    assert '    "test": "succeeded"\n' in capsys.readouterr().out
