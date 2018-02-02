#!/usr/bin/env python
import pika
import sys
from event_writer import config
from collections import namedtuple
from ngcd_common import events_pb2, model


HEADER_CLASS_MAP = {
    'PipelineStarted': events_pb2.PipelineStarted,
    'PipelineFinished': events_pb2.PipelineFinished,
    'PipelineStageStarted': events_pb2.PipelineStageStarted,
    'PipelineStageFinished': events_pb2.PipelineStageFinished,
    'CodePushed': events_pb2.CodePushed
}

def handle_headers(headers_map):
    if not headers_map:
         return None
    header_indicator = headers_map.get('proto-message-type', None)
    if not header_indicator:
        return None
    expected_clz = HEADER_CLASS_MAP.get(header_indicator, None)
    return expected_clz

def make_callback(db_session):
    def callback(ch, method, properties, body):
        expected_clz = handle_headers(properties.headers)
        if not expected_clz:
            print('Dont know how to handle message with headers {}, throwing it away'.format(properties.headers))
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return

        parsed_data = parse_message(body, expected_clz)
        print('Received 1 message with routing key {}, of type {}, Data: {}'.format(method.routing_key, expected_clz.__name__, parsed_data))
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
    created_queue_name = create_queue(channel, exchange, queue_name, routing_key)
    channel.basic_consume(make_callback(db_session),
                          queue=created_queue_name)

def parse_message(data, expected_clz):
    message = expected_clz()
    message.ParseFromString(data)

    return message

def main():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.orm import sessionmaker
    db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=db_engine))

    model.Base.query = db_session.query_property()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    model.Base.metadata.drop_all(db_engine)
    model.Base.metadata.create_all(db_engine)

    print('Setting up queue workers')
    setup_listener(db_session, channel, 'internal', 'internal.pipeline.all', 'pipeline.#')
    setup_listener(db_session, channel, 'internal', 'internal.scm.all', 'scm.#')
    print(' [*] Waiting for data. To exit press CTRL+C')

    channel.start_consuming()

if __name__ == '__main__':
    main()
