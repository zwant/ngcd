#!/usr/bin/env python
import pika
import sys
from sqlalchemy_utils.functions import database_exists, create_database
from collections import namedtuple
from ngcd_common import queue_configs, model
import logging
import os

logger = logging.getLogger('event_writer')

def make_callback(db_session):
    def callback(ch, method, properties, body):
        expected_clz = queue_configs.handle_headers(properties.headers)
        if not expected_clz:
            logger.warn('Dont know how to handle message with headers [%s], throwing it away', properties.headers)
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return

        parsed_data = parse_message(body, expected_clz)
        logger.debug('Received 1 message with routing key [%s], of type [%s]', method.routing_key, expected_clz.__name__)
        model.Event.write_event(db_session, parsed_data)
        ch.basic_ack(delivery_tag = method.delivery_tag)
    return callback

def create_queue(channel, exchange, queue_name, routing_key):
    queue_result = channel.queue_declare(queue_name, durable=True)
    channel.queue_bind(exchange=exchange,
                       queue=queue_result.method.queue,
                       routing_key=routing_key)

    return queue_result.method.queue

def setup_listener(db_session, channel, exchange, queue_name, routing_key):
    logger.info('Setting up listener on exchange [%s], queue [%s] with routing key [%s]', exchange, queue_name, routing_key)
    created_queue_name = create_queue(channel, exchange, queue_name, routing_key)
    channel.basic_consume(make_callback(db_session),
                          queue=created_queue_name)

def parse_message(data, expected_clz):
    message = expected_clz()
    message.ParseFromString(data)

    return message

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

    connection_established = False

    while not connection_established:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_HOST))
            connection_established = True
        except pika.exceptions.ConnectionClosed:
            logger.error('Unable to connect to RabbitMQ host [%s]. Will retry in a second!', config.RABBITMQ_HOST)
            import time
            time.sleep(1)

    channel = connection.channel()
    if config.CLEAN_DB == True:
        logger.info('Cleaning DB')
        model.Base.metadata.drop_all(db_engine)
    else:
        logger.info('Not cleaning DB')
    model.Base.metadata.create_all(db_engine)

    logger.info('Setting up queue workers')
    setup_listener(db_session, channel, 'internal', 'internal.pipeline.all', 'pipeline.#')
    setup_listener(db_session, channel, 'internal', 'internal.scm.all', 'scm.#')
    setup_listener(db_session, channel, 'internal', 'internal.artifact.all', 'artifact.#')
    logger.info('[*] Connected to RabbitMQ at [%s]. Waiting for data. To exit press CTRL+C', config.RABBITMQ_HOST)

    channel.start_consuming()

if __name__ == '__main__':
    main()
