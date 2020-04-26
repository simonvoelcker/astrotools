import argparse

from flask import Flask
from flask_cors import CORS

from hti.server.config import Production
from hti.server.client import api_blueprint, client_blueprint


app = Flask(__name__)
CORS(app)

config = Production
app.register_blueprint(api_blueprint)
app.register_blueprint(client_blueprint)
app.config.from_object(config)
app.secret_key = app.config['FLASK_SECRET_KEY']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'], debug=app.config['FLASK_DEBUG'])
