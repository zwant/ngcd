from flask_env import MetaFlaskEnv


class Configuration(metaclass=MetaFlaskEnv):
    # Enable Flask's debugging features. Should be False in production
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5432/event_api'
    SQLALCHEMY_TRACK_MODIFICATIONS = 'false'
    CLEAN_DB = False
