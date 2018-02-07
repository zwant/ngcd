class Configuration(object):
    RABBITMQ_HOST = "localhost"
    LOGCONFIG = 'validator/logging.yaml'

    def __init__(self, env):
        if 'RABBITMQ_HOST' in env:
            self.RABBITMQ_HOST = env['RABBITMQ_HOST']
