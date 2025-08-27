import logging
import os
import traceback
from pathlib import Path

from flask import Flask
from flask_restful import Api, Resource

from helperFunctions.config import load_config
from helperFunctions.file_system import change_owner_of_output_files
from helperFunctions.program_setup import setup_logging
from unpacker.unpack import Unpacker
from unpacker.unpackBase import UnpackBase

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
            input_file = list(input_dir.iterdir())[0]
            unpacker = Unpacker(config, folder=folder, base=self.unpacking_base)
            unpacker.unpack(input_file)
            if self.owner:
                change_owner_of_output_files(input_dir.parent, self.owner)
        except Exception:  # pylint: disable=broad-except
            return str(traceback.format_exc()), 400

        return '', 200


@api.resource('/status', methods=['GET'])
class StatusRoute(Resource):
    def get(self):
        return '', 200
