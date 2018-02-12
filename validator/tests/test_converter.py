from validator.run import Worker
from ngcd_common import events_pb2, queue_configs
from google.protobuf.timestamp_pb2 import Timestamp
from kombu import Queue, Consumer, Producer
from time import sleep

def timestamp_from_json_string(json_string):
    ts = Timestamp()
    ts.FromJsonString(json_string)

    return ts

def publish_msg_and_get_from_other_queue(amqp_connection,
                                         proto_obj,
                                         src_queue,
                                         dst_queue,
                                         headers,
                                         expected_number_of_output_msgs=1):
    received_msgs = []
    def on_message(self, message):
        received_msgs.append(message)

    worker = Worker(amqp_connection)
    with amqp_connection.channel() as channel:
        producer = Producer(channel)
        result = producer.publish(proto_obj.SerializeToString(),
            exchange=queue_configs.EXTERNAL_EXCHANGE,
            routing_key=src_queue.routing_key,
            content_type='application/vnd.google.protobuf',
            content_encoding='binary',
            headers=headers,
            delivery_mode=2,
            declare=[queue_configs.EXTERNAL_EXCHANGE, src_queue]
        )

    [_ for _ in worker.consume(limit=expected_number_of_output_msgs)]
    with Consumer(amqp_connection, dst_queue, callbacks=[on_message]):
        amqp_connection.drain_events(timeout=1)

    return received_msgs

class TestConverter(object):
    def test_forwards_pipeline_started(self, amqp_connection):
        ts = timestamp_from_json_string("2012-04-23T18:25:43.511Z")
        event = events_pb2.PipelineStarted(uuid="abcdef",
                                           timestamp=ts)
        headers = {"proto-message-type": 'PipelineStarted'}
        received_msgs = publish_msg_and_get_from_other_queue(amqp_connection,
                                                             event,
                                                             queue_configs.EXTERNAL_QUEUES['pipeline.started'],
                                                             queue_configs.INTERNAL_QUEUES['pipeline.started'],
                                                             headers)
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
