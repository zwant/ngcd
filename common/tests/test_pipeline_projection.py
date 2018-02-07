from ngcd_common.projections import PipelineProjection
from ngcd_common.model import Pipeline as PipelineModel
import dateutil.parser

class Container(object):
    pass

def apply_events(func, model, events):
    for event in events:
        func(model, event)

class TestPipelineProjection(object):
    def test_apply_pipeline_started_event_to_empty(self):
        event = Container()
        event.type = 'PipelineStarted'
        event.body = {
            'timestamp': '2017-02-02T14:25:43.511Z'
        }
        model = PipelineModel(external_id='test')
        apply_events(PipelineProjection.apply_event_to_model,
                     model,
                     [event])

        assert model.external_id == 'test'
        assert model.currently_running == True
        assert model.result == None
        assert model.last_update == '2017-02-02T14:25:43.511Z'
        assert model.started_running_at == '2017-02-02T14:25:43.511Z'
        assert model.number_of_runs == 0

    def test_apply_started_and_finished_events_to_empty(self):
        event1 = Container()
        event1.type = 'PipelineStarted'
        event1.body = {
            'timestamp': '2017-02-02T14:25:43.511Z'
        }

        event2 = Container()
        event2.type = 'PipelineFinished'
        event2.body = {
            'timestamp': '2017-02-02T15:25:43.511Z',
            'durationMs': 1000,
            'result': 'ABORTED'
        }
        model = PipelineModel(external_id='test')
        apply_events(PipelineProjection.apply_event_to_model,
                     model,
                     [event1, event2])

        assert model.external_id == 'test'
        assert model.currently_running == False
        assert model.result == 'ABORTED'
        assert model.last_update == '2017-02-02T15:25:43.511Z'
        assert model.started_running_at == '2017-02-02T14:25:43.511Z'
        assert model.finished_running_at == '2017-02-02T15:25:43.511Z'
        assert model.average_duration == 1000
        assert model.number_of_runs == 1
        assert model.last_duration == 1000

    def test_apply_multiple_runs_to_empty(self):
        event1 = Container()
        event1.type = 'PipelineStarted'
        event1.body = {
            'timestamp': '2017-02-02T14:25:43.511Z'
        }

        event2 = Container()
        event2.type = 'PipelineFinished'
        event2.body = {
            'timestamp': '2017-02-02T15:25:43.511Z',
            'durationMs': 1000,
            'result': 'ABORTED'
        }

        event3 = Container()
        event3.type = 'PipelineStarted'
        event3.body = {
            'timestamp': '2017-02-03T14:25:43.511Z'
        }

        event4 = Container()
        event4.type = 'PipelineFinished'
        event4.body = {
            'timestamp': '2017-02-03T15:25:43.511Z',
            'durationMs': 500,
            'result': 'SUCCESS'
        }
        model = PipelineModel(external_id='test')
        apply_events(PipelineProjection.apply_event_to_model,
                     model,
                     [event1, event2, event3, event4])

        assert model.external_id == 'test'
        assert model.currently_running == False
        assert model.result == 'SUCCESS'
        assert model.last_update == '2017-02-03T15:25:43.511Z'
        assert model.started_running_at == '2017-02-03T14:25:43.511Z'
        assert model.finished_running_at == '2017-02-03T15:25:43.511Z'
        assert model.average_duration == 750
        assert model.number_of_runs == 2
        assert model.last_duration == 500
