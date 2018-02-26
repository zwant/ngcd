from flask_env import MetaFlaskEnv


class Configuration(metaclass=MetaFlaskEnv):
    # Enable Flask's debugging features. Should be False in production
    DEBUG = True

    # Examples:
    #PROJECTION_SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5433/event_api'
    PROJECTION_SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/projections.db'
    # Valid values for PROJECTION_STORE_BACKEND_TYPE:
    # inmemory
    # sqlalchemy
    PROJECTION_STORE_BACKEND_TYPE = 'sqlalchemy'
    #PROJECTION_STORE_BACKEND_TYPE = 'inmemory'
    # Valid values for EVENT_STORE_BACKEND_TYPE:
    # dummy - will return fake data for testing
    # sqlalchemy
    #EVENT_STORE_BACKEND_TYPE = 'sqlalchemy'
    EVENT_STORE_BACKEND_TYPE = 'dummy'
    EVENT_SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5433/event_api'
    CLEAN_PROJECTION_DB = True
    LOGCONFIG = 'event_api/logging.yaml'
    LOGGER_HANDLER_POLICY = 'always'
    LOGGER_NAME = 'event_api'
