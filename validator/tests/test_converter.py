from validator.run import Worker, internal_exchange, external_exchange
from ngcd_common import events_pb2
from google.protobuf.timestamp_pb2 import Timestamp
from kombu import Queue, Consumer, Producer
from time import sleep

def timestamp_from_json_string(json_string):
    ts = Timestamp()
    ts.FromJsonString(json_string)

    return ts

class TestConverter(object):
    def test_forwards_pipeline_started(self, amqp_connection):
        expected_input_queue = Queue('external.pipeline.started',
                                     exchange=external_exchange, routing_key='pipeline.started')
        expected_output_queue = Queue('internal.pipeline.started',
                                      exchange=internal_exchange, routing_key='pipeline.started')
        received_msgs = []
        def on_message(self, message):
            received_msgs.append(message)

        worker = Worker(amqp_connection)
        with amqp_connection.channel() as channel:
            producer = Producer(channel)
            ts = timestamp_from_json_string("2012-04-23T18:25:43.511Z")
            event = events_pb2.PipelineStarted(uuid="abcdef",
                                               timestamp=ts)
            result = producer.publish(event.SerializeToString(),
                exchange=external_exchange,
                routing_key="pipeline.started",
                content_type='application/vnd.google.protobuf',
                content_encoding='binary',
                headers={"proto-message-type": 'PipelineStarted'},
                delivery_mode=2,
                declare=[external_exchange, expected_input_queue]
            )

        [_ for _ in worker.consume(limit=1)]
        with Consumer(amqp_connection, expected_output_queue, callbacks=[on_message]):
            amqp_connection.drain_events(timeout=1)

        assert len(received_msgs) == 1
        msg = received_msgs[0]
        assert msg.content_type == 'application/vnd.google.protobuf'
        assert msg.headers == {"proto-message-type": 'PipelineStarted'}
        assert msg.delivery_info['routing_key'] == 'pipeline.started'

        data = events_pb2.PipelineStarted()
        data.ParseFromString(msg.body)
        assert data.uuid == 'abcdef'

    def test_build_headers(self):
        worker = Worker(None)
        assert worker.build_headers(events_pb2.PipelineStarted) == {'proto-message-type': 'PipelineStarted'}
        assert worker.build_headers(events_pb2.CodePushed) == {'proto-message-type': 'CodePushed'}
