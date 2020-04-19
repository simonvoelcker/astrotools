import os


class Config:
    TESTING = False
    PRODUCTION = False

    FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'UnsafeSecret')


class Testing(Config):
    TESTING = True


class Production(Config):
    PRODUCTION = True


config_by_name = dict(
    testing=Testing,
    production=Production
)
