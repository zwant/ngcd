from validator import run
from ngcd_common import events_pb2
from google.protobuf.timestamp_pb2 import Timestamp
import pika

class TestConverter(object):
    def setup_channel_mock(self, mocker, expected_queue_name):
        rabbitmq_channel_mock = mocker.MagicMock()
        rabbitmq_channel_mock.queue_declare.return_value.method.queue = expected_queue_name

        return rabbitmq_channel_mock

    def test_create_queue_from_config(self, mocker):
        expected_queue_name = 'external.pipeline.started'
        queue_config = run.QueueConfig('external',
                                       expected_queue_name,
                                       'pipeline.started',
                                       events_pb2.PipelineStarted)
        rabbitmq_channel_mock = self.setup_channel_mock(mocker, expected_queue_name)
        returned = run.create_queue_from_config(rabbitmq_channel_mock, queue_config)

        rabbitmq_channel_mock.queue_declare.assert_called_once_with(expected_queue_name, durable=True)
        rabbitmq_channel_mock.queue_bind.assert_called_once_with(exchange='external',
                           queue=expected_queue_name,
                           routing_key='pipeline.started')
        assert returned == "external.pipeline.started"

    def test_setup_converter(self, mocker):
        expected_queue_name = 'external.pipeline.started'
        src_queue_config = run.QueueConfig('external',
                                       'external.pipeline.started',
                                       'pipeline.started',
                                       events_pb2.PipelineStarted)
        dst_queue_config = run.QueueConfig('internal',
                                       'internal.pipeline.started',
                                       'pipeline.started',
                                       events_pb2.PipelineStarted)
        rabbitmq_channel_mock = self.setup_channel_mock(mocker, expected_queue_name)
        mocker.spy(run, 'create_callback')

        run.setup_converter(rabbitmq_channel_mock, src_queue_config, dst_queue_config)

        rabbitmq_channel_mock.queue_declare.assert_called_once_with(expected_queue_name, durable=True)
        rabbitmq_channel_mock.queue_bind.assert_called_once_with(exchange='external',
                           queue=expected_queue_name,
                           routing_key='pipeline.started')
        rabbitmq_channel_mock.basic_consume.assert_called_once_with(mocker.ANY, queue=expected_queue_name)

        run.create_callback.assert_called_once_with(src_queue_config, dst_queue_config)

    def test_create_callback(self, mocker):
        src_queue_config = run.QueueConfig('external',
                                       'external.pipeline.started',
                                       'pipeline.started',
                                       events_pb2.PipelineStarted)
        dst_queue_config = run.QueueConfig('internal',
                                       'internal.pipeline.started',
                                       'route_key.pipeline.started',
                                       events_pb2.PipelineStarted)

        rabbitmq_channel_mock = mocker.MagicMock()
        ts = Timestamp()
        ts.FromJsonString("2017-02-03T12:02:43.511Z")
        msg_body = events_pb2.PipelineStarted(uuid="12345",
                                              timestamp=ts).SerializeToString()
        callback_method = run.create_callback(src_queue_config, dst_queue_config)
        callback_method(rabbitmq_channel_mock, mocker.MagicMock(), mocker.MagicMock(), msg_body)
        rabbitmq_channel_mock.basic_ack.assert_called_once()
        rabbitmq_channel_mock.basic_publish.assert_called_once_with(
            exchange="internal",
             routing_key="route_key.pipeline.started",
             body=msg_body,
             properties=mocker.ANY
        )

    def test_build_headers(self, mocker):
        queue_config = run.QueueConfig('internal',
                                       'internal.pipeline.started',
                                       'route_key.pipeline.started',
                                       events_pb2.PipelineStarted)
        assert run.get_headers(queue_config) == {'proto-message-type': 'PipelineStarted'}

        queue_config = run.QueueConfig('internal',
                                       'internal.pipeline.started',
                                       'route_key.pipeline.started',
                                       events_pb2.CodePushed)
        assert run.get_headers(queue_config) == {'proto-message-type': 'CodePushed'}
