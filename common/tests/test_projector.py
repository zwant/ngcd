from ngcd_common.projections.projector import Projector
from ngcd_common.projections.backends import SQLAlchemyBackend, InMemoryBackend
from ngcd_common import model, events_pb2
from google.protobuf.timestamp_pb2 import Timestamp
import dateutil.parser

def timestamp_from_json_string(json_string):
    ts = Timestamp()
    ts.FromJsonString(json_string)

    return ts

def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    for backend in metafunc.cls.backends:
        idlist.append(backend[0])
        items = backend[1].items()
        argnames = [x[0] for x in items]
        argvalues.append(([x[1] for x in items]))
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")

sqlalchemy_backend = ('sqlalchemy', {'backend_name': 'sqlalchemy'})
in_memory_backend = ('in_memory', {'backend_name': 'in_memory'})

def get_backend(name, db_session):
    if name == 'sqlalchemy':
        return SQLAlchemyBackend(db_session)
    else:
        return InMemoryBackend()

class TestProjector(object):
    backends = [sqlalchemy_backend, in_memory_backend]

    def test_pipeline_currently_running(self, backend_name, session):
        ts = timestamp_from_json_string("2017-02-02T14:25:43.511Z")
        event = events_pb2.PipelineStarted(uuid="test1",
                                           timestamp=ts)
        model.Event.write_event(session, event)

        backend = get_backend(backend_name, session)
        projector = Projector(backend, session)
        projector.process_events()

        pipeline = backend.get_one_by_external_id("test1", model.Pipeline)
        assert pipeline is not None
        assert pipeline.external_id == 'test1'
        assert pipeline.currently_running == True
        assert pipeline.result == None

    def test_pipeline_finished_success(self, backend_name, session):
        event = events_pb2.PipelineStarted(uuid="test1",
                                           timestamp=timestamp_from_json_string("2017-02-02T14:25:43.511Z"))
        model.Event.write_event(session, event)

        event = events_pb2.PipelineFinished(uuid="test1",
                                           timestamp=timestamp_from_json_string("2017-02-02T14:26:43.511Z"),
                                           duration_ms=100,
                                           result=events_pb2.SUCCESS)
        model.Event.write_event(session, event)

        backend = get_backend(backend_name, session)
        projector = Projector(backend, session)
        projector.process_events()

        pipeline = backend.get_one_by_external_id("test1", model.Pipeline)
        assert pipeline is not None
        assert pipeline.external_id == 'test1'
        assert pipeline.currently_running == False
        assert pipeline.result == "SUCCESS"
        assert pipeline.started_running_at == dateutil.parser.parse("2017-02-02T14:25:43.511Z")
        assert pipeline.finished_running_at == dateutil.parser.parse("2017-02-02T14:26:43.511Z")

    def test_stage_only_applies_to_same_pipeline(self, backend_name, session):
        # First pipeline
        event = events_pb2.PipelineStarted(uuid="test1",
                                           timestamp=timestamp_from_json_string("2017-02-02T14:25:43.511Z"))
        model.Event.write_event(session, event)

        event = events_pb2.PipelineFinished(uuid="test1",
                                           timestamp=timestamp_from_json_string("2017-02-02T14:26:43.511Z"),
                                           duration_ms=100,
                                           result=events_pb2.SUCCESS)
        model.Event.write_event(session, event)

        # Second pipeline
        event = events_pb2.PipelineStarted(uuid="test2",
                                           timestamp=timestamp_from_json_string("2017-02-02T14:25:43.511Z"))
        model.Event.write_event(session, event)

        event = events_pb2.PipelineFinished(uuid="test2",
                                           timestamp=timestamp_from_json_string("2017-02-02T14:26:43.511Z"),
                                           duration_ms=100,
                                           result=events_pb2.SUCCESS)
        model.Event.write_event(session, event)

        # Correct Stage
        event = events_pb2.PipelineStageStarted(uuid="stage1",
                                                pipeline_uuid='test1',
                                                timestamp=timestamp_from_json_string("2017-02-02T14:25:43.511Z"))
        model.Event.write_event(session, event)

        event = events_pb2.PipelineStageFinished(uuid="stage1",
                                                 pipeline_uuid='test1',
                                                 timestamp=timestamp_from_json_string("2017-02-02T14:26:43.511Z"),
                                                 duration_ms=100,
                                                 result=events_pb2.SUCCESS)
        model.Event.write_event(session, event)

        # Wrong Stage
        event = events_pb2.PipelineStageStarted(uuid="stage1",
                                                pipeline_uuid='test2',
                                                timestamp=timestamp_from_json_string("2017-02-02T14:25:43.511Z"))
        model.Event.write_event(session, event)

        event = events_pb2.PipelineStageFinished(uuid="stage1",
                                                 pipeline_uuid='test2',
                                                 timestamp=timestamp_from_json_string("2017-02-02T14:26:43.511Z"),
                                                 duration_ms=1000,
                                                 result=events_pb2.ABORTED)
        model.Event.write_event(session, event)

        backend = get_backend(backend_name, session)
        projector = Projector(backend, session)
        projector.process_events()

        pipeline_stage = backend.get_one_by_filter(model.PipelineStage, {"pipeline_id": "test1",
                                                                     "external_id": "stage1"})
        assert pipeline_stage is not None
        assert pipeline_stage.external_id == 'stage1'
        assert pipeline_stage.pipeline_id == 'test1'
        assert pipeline_stage.currently_running == False
        assert pipeline_stage.result == "SUCCESS"
        assert pipeline_stage.started_running_at == dateutil.parser.parse("2017-02-02T14:25:43.511Z")
        assert pipeline_stage.finished_running_at == dateutil.parser.parse("2017-02-02T14:26:43.511Z")
