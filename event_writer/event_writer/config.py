RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = "5672"
RABBITMQ_EXCHANGE = 'internal'
RABBITMQ_QUEUE = 'internal.pipeline'
RABBITMQ_ROUTING_KEY = 'pipeline.#'

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5432/event_api'
SQLALCHEMY_TRACK_MODIFICATIONS = 'false'
