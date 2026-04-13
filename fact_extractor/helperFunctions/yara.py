from __future__ import annotations

import logging
from pathlib import Path

import yara

_RULE_DIR = Path(__file__).parent.parent / 'signatures/file_types'
_COMPILED_RULES = _RULE_DIR / 'compiled.yarc'
_rule_files = list(_RULE_DIR.glob('*.yara'))
_rule_creation_time = _COMPILED_RULES.stat().st_mtime if _COMPILED_RULES.exists() else 0
try:
    # if any rule file was changed after the compiled rule file, recompile the rules
    if any(f.stat().st_mtime > _rule_creation_time for f in _rule_files):
        _YARA_RULES = yara.compile(filepaths={f.stem: str(f) for f in _rule_files})
        _YARA_RULES.save(str(_COMPILED_RULES))
    else:
        _YARA_RULES = yara.load(str(_COMPILED_RULES))
except SyntaxError:
    logging.error(f'File from {_RULE_DIR} could not be compiled with YARA')
    _YARA_RULES = yara.compile(source='')


def get_yara_magic(path: str | Path) -> str:
    for match in _YARA_RULES.match(str(path)):
        return match.meta.get('MIME', match.rule)
    return 'application/octet-stream'
