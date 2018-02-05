#!/usr/bin/env python
import pika
import sys
from metrics_writer import influx_writer
from ngcd_common import events_pb2, queue_configs
from influxdb import InfluxDBClient

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    influxdb_connection = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')
    influxdb_connection.create_database('example')
    print('Setting up listener')
    setup_listener(channel, influxdb_connection)
    print(' [*] Waiting for data. To exit press CTRL+C')

    channel.start_consuming()

def create_callback(influxdb_connection):
    def callback(ch, method, properties, body):
        expected_clz = queue_configs.handle_headers(properties.headers)
        if not expected_clz:
            print('Dont know how to handle message with headers {}, throwing it away'.format(properties.headers))
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return

        parsed_data = parse_message(body, expected_clz)
        writing_method = influx_writer.get_writing_method(expected_clz.__name__)
        if writing_method:
            writing_method(influxdb_connection, parsed_data)
        else:
            print('Ignored message with routing key {}, of type {}'.format(method.routing_key, expected_clz.__name__))
        ch.basic_ack(delivery_tag = method.delivery_tag)

        print('Received 1 message with routing key {}, of type {}'.format(method.routing_key, expected_clz.__name__))
    return callback

def create_queue(channel):
    queue_result = channel.queue_declare('internal.metrics.all', durable=True)
    channel.queue_bind(exchange='internal',
                       queue=queue_result.method.queue,
                       routing_key='#')

    return queue_result.method.queue

def setup_listener(channel, influxdb_connection):
    created_queue_name = create_queue(channel)
    channel.basic_consume(create_callback(influxdb_connection),
                          queue=created_queue_name)

def parse_message(data, expected_clz):
    message = expected_clz()
    message.ParseFromString(data)

    return message

if __name__ == '__main__':
    main()
