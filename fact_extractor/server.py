from __future__ import annotations

import logging
import os
import traceback
from pathlib import Path

from flask import Flask, request
from flask_restful import Api, Resource

from helperFunctions.config import load_config
from helperFunctions.file_system import change_owner_of_output_files
from helperFunctions.program_setup import setup_logging
from unpacker.unpack import Unpacker
from unpacker.unpackBase import UnpackBase

# features supported by this extractor version (can be checked by FACT using the /status endpoint)
FEATURES = ['input_path']

app = Flask(__name__)
api = Api(app)
config = load_config('main.cfg')
setup_logging(False, log_level=int(os.getenv('LOG_LEVEL', logging.WARNING)))


@api.resource('/start/<folder>', methods=['GET'])
class RestRoute(Resource):
    def __init__(self):
        self.owner = os.getenv('CHMOD_OWNER', None)
        self.unpacking_base = UnpackBase(config)

    def get(self, folder):
        input_dir = Path(config.get('unpack', 'data_folder'), folder, 'input')
        try:
            input_file = _get_input_file(input_dir, request.args.get('input'))
            unpacker = Unpacker(config, folder=folder, base=self.unpacking_base)
            unpacker.unpack(str(input_file))
            if self.owner:
                change_owner_of_output_files(input_dir.parent, self.owner)
        except Exception:  # pylint: disable=broad-except
            return str(traceback.format_exc()), 400

        return '', 200


def _get_input_file(input_dir: Path, input_path: str | None) -> Path:
    """
    If `input_path` is set, the input file is read directly from the (read-only) firmware storage folder, which
    avoids copying the file to the shared folder. Otherwise, the (single) file in the input folder is used.
    """
    if input_path is None:
        return next(input_dir.iterdir())
    storage_dir = Path(config.get('unpack', 'firmware_storage_folder')).resolve()
    input_file = (storage_dir / input_path).resolve()
    if not input_file.is_relative_to(storage_dir):
        raise ValueError(f'Input path {input_path} is outside of the firmware storage folder')
    if not input_file.is_file():
        raise FileNotFoundError(f'Input file {input_path} not found in the firmware storage folder')
    return input_file


@api.resource('/status', methods=['GET'])
class StatusRoute(Resource):
    def get(self):
        return {'features': FEATURES}, 200
