from flask_env import MetaFlaskEnv


class Configuration(metaclass=MetaFlaskEnv):
    # Enable Flask's debugging features. Should be False in production
    DEBUG = True

    RABBITMQ_HOST = "localhost"
    RABBITMQ_PORT = "5672"
