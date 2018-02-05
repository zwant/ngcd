#!/usr/bin/env python
import pika
import sys
from collections import namedtuple
from ngcd_common import events_pb2

QueueConfig = namedtuple('QueueConfig', ['exchange', 'name', 'routing_key', 'message_clz'])

ALL_QUEUE_CONFIGS = [
    (QueueConfig('external', 'external.pipeline.started', 'pipeline.started', events_pb2.PipelineStarted),
     QueueConfig('internal', 'internal.pipeline.started', 'pipeline.started', events_pb2.PipelineStarted)),

    (QueueConfig('external', 'external.pipeline.finished', 'pipeline.finished', events_pb2.PipelineFinished),
     QueueConfig('internal', 'internal.pipeline.finished', 'pipeline.finished', events_pb2.PipelineFinished)),

    (QueueConfig('external', 'external.pipeline.stage.started', 'pipeline.stage.started', events_pb2.PipelineStageStarted),
     QueueConfig('internal', 'internal.pipeline.stage.started', 'pipeline.stage.started', events_pb2.PipelineStageStarted)),

    (QueueConfig('external', 'external.pipeline.stage.finished', 'pipeline.stage.finished', events_pb2.PipelineStageFinished),
     QueueConfig('internal', 'internal.pipeline.stage.finished', 'pipeline.stage.finished', events_pb2.PipelineStageFinished)),

    (QueueConfig('external', 'external.scm.repo.push', 'scm.repo.push', events_pb2.CodePushed),
     QueueConfig('internal', 'internal.scm.repo.push', 'scm.repo.push', events_pb2.CodePushed)),
]
def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='internal',
                             durable=True,
                             exchange_type='topic')

    print('Setting up {} converters'.format(len(ALL_QUEUE_CONFIGS)))
    for src_config, dst_config in ALL_QUEUE_CONFIGS:
        setup_converter(channel, src_config, dst_config)
    print(' [*] Waiting for data. To exit press CTRL+C')

    channel.start_consuming()

def get_headers(queue_config):
    return {'proto-message-type': str(queue_config.message_clz.__name__)}

def create_callback(src_queue_config, dst_queue_config):
    def callback(ch, method, properties, body):
        headers = get_headers(dst_queue_config)
        ch.basic_publish(exchange=dst_queue_config.exchange,
                         routing_key=dst_queue_config.routing_key,
                         body=validate_and_convert_message(body, src_queue_config.message_clz, dst_queue_config.message_clz),
                         properties=pika.BasicProperties(
                            delivery_mode = 2, # make message persistent
                            headers=headers
                         ))
        ch.basic_ack(delivery_tag = method.delivery_tag)
        print('Forwarded 1 message from {} to {}'.format(src_queue_config.name, dst_queue_config.name))
    return callback

def create_queue_from_config(channel, queue_config):
    queue_result = channel.queue_declare(queue_config.name, durable=True)
    channel.queue_bind(exchange=queue_config.exchange,
                       queue=queue_result.method.queue,
                       routing_key=queue_config.routing_key)

    return queue_result.method.queue

def setup_converter(channel, src_queue_config, dst_queue_config):
    created_queue_name = create_queue_from_config(channel, src_queue_config)
    channel.basic_consume(create_callback(src_queue_config, dst_queue_config),
                          queue=created_queue_name)

def validate_and_convert_message(data, expected_clz, output_clz):
    message = expected_clz()
    message.ParseFromString(data)

    return message.SerializeToString()

if __name__ == '__main__':
    main()
