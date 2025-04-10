from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, Generator

import pytest

if TYPE_CHECKING:
    from flask.testing import FlaskClient

TEST_FILE = Path(__file__).parent.parent / 'data' / 'container' / 'test.zip'
EXTRACTION_TEST_DIR = 'extractor_foo123'


@pytest.fixture
def test_dir() -> Generator[Path, Any, None]:
    with TemporaryDirectory() as tmp_dir:
        input_dir = Path(tmp_dir) / EXTRACTION_TEST_DIR / 'input'
        input_dir.mkdir(parents=True)
        (Path(tmp_dir) / EXTRACTION_TEST_DIR / 'reports').mkdir()
        test_file = input_dir / 'test.zip'
        test_file.write_bytes(TEST_FILE.read_bytes())
        yield Path(tmp_dir)


@pytest.fixture
def client(test_dir) -> FlaskClient:
    from server import app, config

    config.set('unpack', 'data_folder', str(test_dir))
    return app.test_client()


def test_server_start(client: FlaskClient, test_dir: Path):
    response = client.get(f'/start/{EXTRACTION_TEST_DIR}')
    assert response.status_code == 200
    extraction_dir = test_dir / EXTRACTION_TEST_DIR
    output_dir = extraction_dir / 'files'
    assert output_dir.is_dir()
    extracted_files = {f.name for f in output_dir.glob('**/*') if f.is_file()}
    assert extracted_files == {'testfile1', 'testfile2', 'test file 3_.txt'}


def test_dir_not_found(client: FlaskClient):
    response = client.get('/start/not_found')
    assert response.status_code == 400


def test_server_status(client: FlaskClient):
    response = client.get('/status')
    assert response.status_code == 200
