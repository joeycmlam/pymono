from flask import Flask
from flask_restful import Resource, Api
from flask_injector import FlaskInjector
from injector import inject
from datetime import datetime
from config import VERSION, NAME

app = Flask(__name__)
api = Api(app)

class Config:
    def __init__(self, name, version):
        self.name = name
        self.version = version

class HealthCheck(Resource):
    @inject
    def __init__(self, config: Config):
        self.config = config

    def get(self):
        return {
            'name': self.config.name,
            'version': self.config.version,
            'datetime': datetime.now().isoformat()
        }

api.add_resource(HealthCheck, '/health')

def configure(binder):
    binder.bind(Config, Config(name=NAME, version=VERSION))

if __name__ == '__main__':
    FlaskInjector(app=app, modules=[configure])
    app.run(port=8080)