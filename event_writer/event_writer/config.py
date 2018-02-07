class Configuration(object):
    RABBITMQ_HOST = "localhost"
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5433/event_api'
    CLEAN_DB = False
    LOGCONFIG = 'event_writer/logging.yaml'

    def __init__(self, env):
        if 'RABBITMQ_HOST' in env:
            self.RABBITMQ_HOST = env['RABBITMQ_HOST']

        if 'SQLALCHEMY_DATABASE_URI' in env:
            self.SQLALCHEMY_DATABASE_URI = env['SQLALCHEMY_DATABASE_URI']

        if 'CLEAN_DB' in env:
            if env['CLEAN_DB'].lower() in ["1", "true"]:
                self.CLEAN_DB = True
