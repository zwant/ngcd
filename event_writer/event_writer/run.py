#!/usr/bin/env python
import pika
import sys
from sqlalchemy_utils.functions import database_exists, create_database
from collections import namedtuple
from ngcd_common import queue_configs, model


def make_callback(db_session):
    def callback(ch, method, properties, body):
        expected_clz = queue_configs.handle_headers(properties.headers)
        if not expected_clz:
            print('Dont know how to handle message with headers {}, throwing it away'.format(properties.headers))
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return

        parsed_data = parse_message(body, expected_clz)
        print('Received 1 message with routing key {}, of type {}'.format(method.routing_key, expected_clz.__name__))
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
    print('Setting up listener on exchange [{}], queue [{}] with routing key [{}]'.format(exchange, queue_name, routing_key))
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

def main():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.orm import sessionmaker

    config = get_config()
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
            print('Unable to connect to RabbitMQ host {}. Will retry in a second!'.format(config.RABBITMQ_HOST))
            import time
            time.sleep(1)

    channel = connection.channel()
    if config.CLEAN_DB == True:
        print('Cleaning DB')
        model.Base.metadata.drop_all(db_engine)
    else:
        print('Not cleaning DB')
    model.Base.metadata.create_all(db_engine)

    print('Setting up queue workers')
    setup_listener(db_session, channel, 'internal', 'internal.pipeline.all', 'pipeline.#')
    setup_listener(db_session, channel, 'internal', 'internal.scm.all', 'scm.#')
    setup_listener(db_session, channel, 'internal', 'internal.artifact.all', 'artifact.#')
    print(' [*] Waiting for data. To exit press CTRL+C')

    channel.start_consuming()

if __name__ == '__main__':
    main()
