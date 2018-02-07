#!/usr/bin/env python
import pika
import sys
import os
from collections import namedtuple
from ngcd_common import events_pb2
import logging

logger = logging.getLogger('validator')

QueueConfig = namedtuple('QueueConfig', ['exchange', 'name', 'routing_key', 'message_clz'])

ALL_QUEUE_CONFIGS = [
     # Pipelines and Stages
    (QueueConfig('external', 'external.pipeline.started', 'pipeline.started', events_pb2.PipelineStarted),
     QueueConfig('internal', 'internal.pipeline.started', 'pipeline.started', events_pb2.PipelineStarted)),

    (QueueConfig('external', 'external.pipeline.finished', 'pipeline.finished', events_pb2.PipelineFinished),
     QueueConfig('internal', 'internal.pipeline.finished', 'pipeline.finished', events_pb2.PipelineFinished)),

    (QueueConfig('external', 'external.pipeline.stage.started', 'pipeline.stage.started', events_pb2.PipelineStageStarted),
     QueueConfig('internal', 'internal.pipeline.stage.started', 'pipeline.stage.started', events_pb2.PipelineStageStarted)),

    (QueueConfig('external', 'external.pipeline.stage.finished', 'pipeline.stage.finished', events_pb2.PipelineStageFinished),
     QueueConfig('internal', 'internal.pipeline.stage.finished', 'pipeline.stage.finished', events_pb2.PipelineStageFinished)),

     # SCM Repos
    (QueueConfig('external', 'external.scm.repo.push', 'scm.repo.push', events_pb2.CodePushed),
     QueueConfig('internal', 'internal.scm.repo.push', 'scm.repo.push', events_pb2.CodePushed)),

    (QueueConfig('external', 'external.scm.repo.create', 'scm.repo.create', events_pb2.RepositoryAdded),
     QueueConfig('internal', 'internal.scm.repo.create', 'scm.repo.create', events_pb2.RepositoryAdded)),

    (QueueConfig('external', 'external.scm.repo.remove', 'scm.repo.remove', events_pb2.RepositoryRemoved),
     QueueConfig('internal', 'internal.scm.repo.remove', 'scm.repo.remove', events_pb2.RepositoryRemoved)),

     # Artifacts
    (QueueConfig('external', 'external.artifact.publish', 'artifact.publish', events_pb2.ArtifactPublished),
     QueueConfig('internal', 'internal.artifact.publish', 'artifact.publish', events_pb2.ArtifactPublished)),

]

def main():
    setup_logging()
    rabbitmq_host = os.environ['RABBITMQ_HOST']
    connection_established = False
    while not connection_established:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            connection_established = True
        except pika.exceptions.ConnectionClosed:
            logger.error('Unable to connect to RabbitMQ host {}. Will retry in a second!'.format(rabbitmq_host))
            import time
            time.sleep(1)

    channel = connection.channel()

    channel.exchange_declare(exchange='external',
                             durable=True,
                             exchange_type='topic')
    channel.exchange_declare(exchange='internal',
                             durable=True,
                             exchange_type='topic')

    logger.info('Setting up {} converters'.format(len(ALL_QUEUE_CONFIGS)))
    for src_config, dst_config in ALL_QUEUE_CONFIGS:
        setup_converter(channel, src_config, dst_config)
    logger.info('[*] Waiting for data. To exit press CTRL+C')

    channel.start_consuming()

def setup_logging():
    import logging.config
    import yaml
    path = 'validator/logging.yaml'
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
            except Exception as e:
                raise Exception('Failed to read log config from {}'.format(path), e)
    else:
        raise Exception('Failed to read log config from {}'.format(path))
    logging.config.dictConfig(config)

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
        logger.debug('Forwarded 1 message from {} to {}'.format(src_queue_config.name, dst_queue_config.name))
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
