import argparse

from flask import Flask

from hti.server.config import Production
from hti.server.client import api_blueprint, client_blueprint


app = Flask(__name__)

config = Production
app.register_blueprint(api_blueprint)
app.register_blueprint(client_blueprint)
app.config.from_object(config)

app.config['bootstrap_version'] = '3.3.7'
app.config['jquery_version'] = '3.1.1'

app.secret_key = app.config['FLASK_SECRET_KEY']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'], debug=app.config['FLASK_DEBUG'])
