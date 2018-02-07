from ngcd_common.projections import PipelineStageProjection
from ngcd_common.model import PipelineStage as PipelineStageModel
import dateutil.parser

class Container(object):
    pass

def apply_events(func, model, events):
    for event in events:
        func(model, event)

class TestPipelineStageProjection(object):
    def test_apply_pipeline_stage_started_event_to_empty(self):
        event = Container()
        event.type = 'PipelineStageStarted'
        event.body = {
            'timestamp': '2017-02-02T14:25:43.511Z',
            'pipelineUuid': 'test-pipeline'
        }
        model = PipelineStageModel(external_id='test-stage')
        apply_events(PipelineStageProjection.apply_event_to_model,
                     model,
                     [event])

        assert model.external_id == 'test-stage'
        assert model.pipeline_id == 'test-pipeline'
        assert model.currently_running == True
        assert model.result == None
        assert model.last_update == '2017-02-02T14:25:43.511Z'
        assert model.started_running_at == '2017-02-02T14:25:43.511Z'
        assert model.number_of_runs == 0

    def test_apply_started_and_finished_events_to_empty(self):
        event1 = Container()
        event1.type = 'PipelineStageStarted'
        event1.body = {
            'timestamp': '2017-02-02T14:25:43.511Z',
            'pipelineUuid': 'test-pipeline'
        }

        event2 = Container()
        event2.type = 'PipelineStageFinished'
        event2.body = {
            'timestamp': '2017-02-02T15:25:43.511Z',
            'pipelineUuid': 'test-pipeline',
            'durationMs': 1000,
            'result': 'ABORTED'
        }
        model = PipelineStageModel(external_id='test-stage')
        apply_events(PipelineStageProjection.apply_event_to_model,
                     model,
                     [event1, event2])

        assert model.external_id == 'test-stage'
        assert model.pipeline_id == 'test-pipeline'
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
        event1.type = 'PipelineStageStarted'
        event1.body = {
            'timestamp': '2017-02-02T14:25:43.511Z',
            'pipelineUuid': 'test-pipeline'
        }

        event2 = Container()
        event2.type = 'PipelineStageFinished'
        event2.body = {
            'timestamp': '2017-02-02T15:25:43.511Z',
            'pipelineUuid': 'test-pipeline',
            'durationMs': 1000,
            'result': 'ABORTED'
        }

        event3 = Container()
        event3.type = 'PipelineStageStarted'
        event3.body = {
            'timestamp': '2017-02-03T14:25:43.511Z',
            'pipelineUuid': 'test-pipeline'
        }

        event4 = Container()
        event4.type = 'PipelineStageFinished'
        event4.body = {
            'timestamp': '2017-02-03T15:25:43.511Z',
            'pipelineUuid': 'test-pipeline',
            'durationMs': 500,
            'result': 'SUCCESS'
        }
        model = PipelineStageModel(external_id='test-stage')
        apply_events(PipelineStageProjection.apply_event_to_model,
                     model,
                     [event1, event2, event3, event4])

        assert model.external_id == 'test-stage'
        assert model.pipeline_id == 'test-pipeline'
        assert model.currently_running == False
        assert model.result == 'SUCCESS'
        assert model.last_update == '2017-02-03T15:25:43.511Z'
        assert model.started_running_at == '2017-02-03T14:25:43.511Z'
        assert model.finished_running_at == '2017-02-03T15:25:43.511Z'
        assert model.average_duration == 750
        assert model.number_of_runs == 2
        assert model.last_duration == 500
