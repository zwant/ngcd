#!/usr/bin/env python
import logging
import os
import sys
from ngcd_common import events_pb2, queue_configs
from kombu import Producer, Queue, Exchange, Connection
from kombu.mixins import ConsumerProducerMixin

logger = logging.getLogger('validator')

ALL_QUEUE_CONFIGS = [
     # Pipelines and Stages
    ((queue_configs.EXTERNAL_QUEUES['pipeline.started'], events_pb2.PipelineStarted),
     (queue_configs.INTERNAL_QUEUES['pipeline.started'], events_pb2.PipelineStarted)),
    ((queue_configs.EXTERNAL_QUEUES['pipeline.finished'], events_pb2.PipelineFinished),
     (queue_configs.INTERNAL_QUEUES['pipeline.finished'], events_pb2.PipelineFinished)),
    ((queue_configs.EXTERNAL_QUEUES['pipeline.stage.started'], events_pb2.PipelineStageStarted),
     (queue_configs.INTERNAL_QUEUES['pipeline.stage.started'], events_pb2.PipelineStageStarted)),
    ((queue_configs.EXTERNAL_QUEUES['pipeline.stage.finished'], events_pb2.PipelineStageFinished),
     (queue_configs.INTERNAL_QUEUES['pipeline.stage.finished'], events_pb2.PipelineStageFinished)),

    # SCM Repos
    ((queue_configs.EXTERNAL_QUEUES['scm.repo.push'], events_pb2.CodePushed),
     (queue_configs.INTERNAL_QUEUES['scm.repo.push'], events_pb2.CodePushed)),
    ((queue_configs.EXTERNAL_QUEUES['scm.repo.create'], events_pb2.RepositoryAdded),
     (queue_configs.INTERNAL_QUEUES['scm.repo.create'], events_pb2.RepositoryAdded)),
    ((queue_configs.EXTERNAL_QUEUES['scm.repo.remove'], events_pb2.RepositoryRemoved),
     (queue_configs.INTERNAL_QUEUES['scm.repo.remove'], events_pb2.RepositoryRemoved)),

     # Artifacts
     ((queue_configs.EXTERNAL_QUEUES['scm.artifact.publish'], events_pb2.ArtifactPublished),
      (queue_configs.INTERNAL_QUEUES['scm.artifact.publish'], events_pb2.ArtifactPublished)),

]

class Worker(ConsumerProducerMixin):

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        logger.info('Setting up [%s] converters', len(ALL_QUEUE_CONFIGS))
        return [Consumer(src_queue,
                         accept=['application/vnd.google.protobuf'],
                         on_message=self.create_callback(src_queue, src_clz, dst_queue, dst_clz)) for ((src_queue, src_clz), (dst_queue, dst_clz)) in ALL_QUEUE_CONFIGS]

    def build_headers(self, message_clz):
        return {'proto-message-type': str(message_clz.__name__)}

    def validate_and_convert_message(self, data, expected_clz, output_clz):
        message = expected_clz()
        message.ParseFromString(data)

        return message.SerializeToString()

    def create_callback(self, src_queue, src_clz, dst_queue, dst_clz):
        def callback(message):
            headers = self.build_headers(dst_clz)
            outgoing_body = self.validate_and_convert_message(message.body, src_clz, dst_clz)
            self.producer.publish(outgoing_body,
                exchange=dst_queue.exchange,
                routing_key=dst_queue.routing_key,
                content_type='application/vnd.google.protobuf',
                content_encoding='binary',
                headers=headers,
                delivery_mode=2,
                declare=[dst_queue]
            )
            logger.debug('Forwarded 1 message from [%s] to [%s]', src_queue.name, dst_queue.name)
            message.ack()
        return callback

def main():
    config = get_config()
    setup_logging(config)

    with Connection('amqp://guest:guest@{}//'.format(config.RABBITMQ_HOST)) as conn:
        logger.info('[*] Connected to RabbitMQ at [%s]. Waiting for data. To exit press CTRL+C', config.RABBITMQ_HOST)
        Worker(conn).run()


def get_config():
    import os
    from validator.config import Configuration

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
