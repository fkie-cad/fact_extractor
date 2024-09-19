import logging
import os
import traceback
from pathlib import Path

from flask import Flask
from flask_restful import Api, Resource

from fact_extractor.helperFunctions.config import load_config
from fact_extractor.helperFunctions.file_system import change_owner_of_output_files
from fact_extractor.helperFunctions.program_setup import setup_logging
from fact_extractor.unpacker.unpack import unpack

app = Flask(__name__)
api = Api(app)
config = load_config('main.cfg')
setup_logging(False, log_level=int(os.getenv('LOG_LEVEL', logging.WARNING)))  # pylint: disable=invalid-envvar-default


@api.resource('/start/<folder>', methods=['GET'])
class RestRoute(Resource):
    def __init__(self):
        self.owner = os.getenv('CHMOD_OWNER', None)

    def get(self, folder):
        input_dir = Path(config.get('unpack', 'data_folder'), folder, 'input')
        try:
            input_file = list(input_dir.iterdir())[0]
            unpack(file_path=str(input_file), config=config, folder=folder)
            if self.owner:
                change_owner_of_output_files(input_dir.parent, self.owner)
        except Exception:  # pylint: disable=broad-except
            return str(traceback.format_exc()), 400

        return '', 200


@api.resource('/status', methods=['GET'])
class StatusRoute(Resource):
    def get(self):
        return '', 200
