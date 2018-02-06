from ngcd_common.projector import Projector
from ngcd_common import model, events_pb2
from google.protobuf.timestamp_pb2 import Timestamp
import dateutil.parser

def timestamp_from_json_string(json_string):
    ts = Timestamp()
    ts.FromJsonString(json_string)

    return ts

class TestProjector(object):

    def test_pipeline_currently_running(self, mocker, session):
        ts = timestamp_from_json_string("2017-02-02T14:25:43.511Z")
        event = events_pb2.PipelineStarted(uuid="test1",
                                           timestamp=ts)
        model.Event.write_event(session, event)

        projector = Projector(session)
        projector.process_events()

        pipeline = model.Pipeline.query \
                    .filter(model.Pipeline.external_id == "test1") \
                    .first()
        assert pipeline.external_id == 'test1'
        assert pipeline.currently_running == True
        assert pipeline.result == None

    def test_pipeline_finished_success(self, mocker, session):
        event = events_pb2.PipelineStarted(uuid="test1",
                                           timestamp=timestamp_from_json_string("2017-02-02T14:25:43.511Z"))
        model.Event.write_event(session, event)

        event = events_pb2.PipelineFinished(uuid="test1",
                                           timestamp=timestamp_from_json_string("2017-02-02T14:26:43.511Z"),
                                           duration_ms=100,
                                           result=events_pb2.SUCCESS)
        model.Event.write_event(session, event)

        projector = Projector(session)
        projector.process_events()

        pipeline = model.Pipeline.query \
                    .filter(model.Pipeline.external_id == "test1") \
                    .first()

        assert pipeline.external_id == 'test1'
        assert pipeline.currently_running == False
        assert pipeline.result == "SUCCESS"
        assert pipeline.started_running_at == dateutil.parser.parse("2017-02-02T14:25:43.511Z")
        assert pipeline.finished_running_at == dateutil.parser.parse("2017-02-02T14:26:43.511Z")
