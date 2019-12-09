import traceback
from pathlib import Path

from flask import Flask
from flask_restful import Api, Resource

from unpacker.unpack import unpack


class RestRoute(Resource):
    def __init__(self, config):
        self._config = config

    def get(self, folder):
        input_dir = Path(self._config.get('unpack', 'data_folder'), folder, 'input')

        input_file = list(input_dir.iterdir())[0]

        try:
            unpack(file_path=input_file, config=self._config, folder=folder)
        except Exception:
            return str(traceback.format_exc()), 400

        return '', 200


class StatusRoute(Resource):
    def get(self):
        return '', 200


class AppWrapper:
    def __init__(self, config):
        self._config = config

        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_resource(RestRoute, '/start/<folder>', methods=['GET'], resource_class_kwargs={'config': self._config})
        self.api.add_resource(StatusRoute, '/status', methods=['GET'])
