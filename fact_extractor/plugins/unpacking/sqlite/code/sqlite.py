from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

NAME = 'sqlite'
MIME_PATTERNS = ['application/vnd.sqlite3']
VERSION = '0.1.0'


def _find_blob_column(columns: list[dict[str, str]]) -> int | None:
    for col_idx, col_data in enumerate(columns):
        if col_data['type'] == 'BLOB':
            return col_idx
    return None


def _find_path_column(columns: list[dict[str, str]]) -> int | None:
    target_columns = {'path', 'file', 'filename', 'file_name'}
    for col_idx, col_data in enumerate(columns):
        if col_data['name'] in target_columns and col_data['type'] == 'TEXT':
            return col_idx
    return None


def _query_blob_data(
    columns: list[dict[str, str]], blob_column: int, table: str, connection
) -> Iterable[tuple[int, bytes, str | None]]:
    cursor = connection.cursor()
    cursor.execute(f'SELECT * FROM {table};')
    path_col_idx = _find_path_column(columns)
    for row_idx, row_data in enumerate(cursor.fetchall()):
        blob = row_data[blob_column]
        if not blob:
            continue
        path = row_data[path_col_idx] if path_col_idx is not None else None
        yield row_idx, blob, path


def _get_schema(connection) -> dict[str, list[dict[str, str]]]:
    schema = {}
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table, *_ in cursor.fetchall():
        if table == 'sqlite_sequence':
            continue
        cursor.execute(f'PRAGMA table_info({table});')
        for _, name, data_type, *__ in cursor.fetchall():
            schema.setdefault(table, []).append({'name': name, 'type': data_type})
    return schema


def unpack_function(file_path: str, tmp_dir: str):
    output_dir = Path(tmp_dir)
    output = []
    total = 0
    try:
        with sqlite3.connect(file_path) as connection:
            schema = _get_schema(connection)
            for table, columns in schema.items():
                if (blob_column := _find_blob_column(columns)) is not None:
                    for idx, blob, path in _query_blob_data(columns, blob_column, table, connection):
                        blob_column_name = columns[blob_column]['name']
                        file_name = Path(path).name if path else f'db_dump_{table}_{blob_column_name}.{idx}'
                        (output_dir / file_name).write_bytes(blob)
                        output.append(f'extracted column {blob_column} from table {table} to file {file_name}')
                        total += 1
        output.append(f'extracted {total} files from DB')
        return {'output': '\n'.join(output), 'schema': schema}
    except Exception as err:
        return {'output': f'Error: {err}'}


# ----> Do not edit below this line <----
def setup(unpack_tool):
    for item in MIME_PATTERNS:
        unpack_tool.register_plugin(item, (unpack_function, NAME, VERSION))
