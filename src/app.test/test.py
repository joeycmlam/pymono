from flask import Flask
from flask_restful import Resource, Api
from datetime import datetime

app = Flask(__name__)
api = Api(app)

class HealthCheck(Resource):
    def get(self):
        return {
            'version': '1.0.0',
            'datetime': datetime.now().isoformat()
        }

api.add_resource(HealthCheck, '/health')

if __name__ == '__main__':
    app.run(debug=True)