from flask_env import MetaFlaskEnv


class Configuration(metaclass=MetaFlaskEnv):
    # Enable Flask's debugging features. Should be False in production
    DEBUG = True

    # Valid options are:
    # inmemory
    # postgres
    PROJECTION_STORE_BACKEND = 'inmemory'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5433/event_api'
    SQLALCHEMY_TRACK_MODIFICATIONS = 'false'
    CLEAN_DB = False
    LOGCONFIG = 'event_api/logging.yaml'
    LOGGER_HANDLER_POLICY = 'always'
    LOGGER_NAME = 'event_api'
