#!/usr/bin/env python
import pika
import sys
from sqlalchemy_utils.functions import database_exists, create_database
from collections import namedtuple
from ngcd_common import queue_configs, model
from kombu.mixins import ConsumerMixin
from kombu import Queue, Exchange, Connection
import logging
import os

logger = logging.getLogger('event_writer')

QUEUES = [Queue('internal.pipeline.all', exchange=queue_configs.INTERNAL_EXCHANGE, routing_key='pipeline.#'),
          Queue('internal.scm.all', exchange=queue_configs.INTERNAL_EXCHANGE, routing_key='scm.#'),
          Queue('internal.artifact.all', exchange=queue_configs.INTERNAL_EXCHANGE, routing_key='artifact.#')]

class Worker(ConsumerMixin):

    def __init__(self, connection, db_session):
        self.connection = connection
        self.db_session = db_session

    def get_consumers(self, Consumer, channel):
        logger.info('Setting up [%s] listeners', len(QUEUES))

        return [Consumer(QUEUES,
                         accept=['application/vnd.google.protobuf'],
                         on_message=self.on_message)]

    def build_headers(self, message_clz):
        return {'proto-message-type': str(message_clz.__name__)}

    def parse_message(self, data, expected_clz):
        message = expected_clz()
        message.ParseFromString(data)

        return message

    def validate_and_convert_message(self, data, expected_clz, output_clz):
        message = expected_clz()
        message.ParseFromString(data)

        return message.SerializeToString()

    def on_message(self, message):
        expected_clz = queue_configs.handle_headers(message.properties['application_headers'])
        if not expected_clz:
            logger.warn('Dont know how to handle message with headers [%s], throwing it away', message.properties['application_headers'])
            message.ack()
            return

        parsed_data = self.parse_message(message.body, expected_clz)
        logger.debug('Received 1 message with routing key [%s], of type [%s]', message.delivery_info['routing_key'], expected_clz.__name__)
        model.Event.write_event(self.db_session, parsed_data)
        message.ack()


def main():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.orm import sessionmaker

    config = get_config()
    setup_logging(config)
    if not database_exists(config.SQLALCHEMY_DATABASE_URI):
        create_database(config.SQLALCHEMY_DATABASE_URI)

    db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=db_engine))

    model.Base.query = db_session.query_property()
    if config.CLEAN_DB == True:
        logger.info('Cleaning DB')
        model.Base.metadata.drop_all(db_engine)
    else:
        logger.info('Not cleaning DB')

    model.Base.metadata.create_all(db_engine)

    with Connection('amqp://guest:guest@{}//'.format(config.RABBITMQ_HOST)) as conn:
        logger.info('[*] Connected to RabbitMQ at [%s]. Waiting for data. To exit press CTRL+C', config.RABBITMQ_HOST)
        Worker(conn, db_session).run()

def get_config():
    import os
    from event_writer.config import Configuration

    return Configuration(os.environ)

def setup_logging(config):
    import logging.config
    import yaml

    path = config.LOGCONFIG
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
            except Exception as e:
                raise Exception('Failed to read log config from {}'.format(path), e)
    else:
        raise Exception('Failed to read log config from {}'.format(path))
    logging.config.dictConfig(config)

if __name__ == '__main__':
    main()
