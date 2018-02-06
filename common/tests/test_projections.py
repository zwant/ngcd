from ngcd_common.projections import RepositoryProjection, PipelineStageProjection, PipelineProjection
from ngcd_common.model import Pipeline as PipelineModel, PipelineStage as PipelineStageModel, Repository as RepositoryModel
import dateutil.parser

class Container(object):
    pass

def apply_events(func, model, events):
    for event in events:
        func(model, event)

class TestRepositoryProjection(object):
    def test_apply_single_event_to_empty(self):
        event = Container()
        event.type = 'CodePushed'
        event.body = {
            'repositoryName': 'test-repo',
            'newHeadSha': '2',
            'previousHeadSha': '1',
            'pusher': 'test-user',
            'commits': [{"test_commit": "hej"}],
            'timestamp': '2017-02-02T14:25:43.511Z'
        }
        model = RepositoryModel(external_id='test')
        apply_events(RepositoryProjection.apply_event_to_model,
                     model,
                     [event])

        assert model.external_id == 'test'
        assert model.name == 'test-repo'
        assert model.head_sha == '2'
        assert model.previous_head_sha == '1'
        assert len(model.commits) == 1
        assert model.last_pusher == 'test-user'
        assert model.last_update == '2017-02-02T14:25:43.511Z'

    def test_apply_multiple_events_to_empty(self):
        event1 = Container()
        event1.type = 'CodePushed'
        event1.body = {
            'repositoryName': 'test-repo',
            'newHeadSha': '2',
            'previousHeadSha': '1',
            'pusher': 'test-user',
            'commits': [{"test_commit": "hej"}],
            'timestamp': '2017-02-02T14:25:43.511Z'
        }

        event2 = Container()
        event2.type = 'CodePushed'
        event2.body = {
            'repositoryName': 'test-repo',
            'newHeadSha': '3',
            'previousHeadSha': '2',
            'pusher': 'test-user',
            'commits': [{"test_commit": "hej"}],
            'timestamp': '2017-02-02T15:25:43.511Z'
        }

        model = RepositoryModel(external_id='test')
        apply_events(RepositoryProjection.apply_event_to_model,
                     model,
                     [event1, event2])

        assert model.external_id == 'test'
        assert model.name == 'test-repo'
        assert model.head_sha == '3'
        assert model.previous_head_sha == '2'
        assert len(model.commits) == 2
        assert model.last_pusher == 'test-user'
        assert model.last_update == '2017-02-02T15:25:43.511Z'

    def test_apply_single_event_to_pre_existing(self):
        event1 = Container()
        event1.type = 'CodePushed'
        event1.body = {
            'repositoryName': 'test-repo',
            'newHeadSha': '2',
            'previousHeadSha': '1',
            'pusher': 'test-user',
            'commits': [{"test_commit": "hej"}],
            'timestamp': '2017-02-02T15:25:43.511Z'
        }

        model = RepositoryModel(external_id='test',
                                name="hello",
                                last_pusher='old-user',
                                head_sha='123',
                                previous_head_sha='234',
                                last_update='2017-02-02T12:25:43.511Z',
                                commits=[{"test_commit": "hej"}])
        apply_events(RepositoryProjection.apply_event_to_model,
                     model,
                     [event1])

        assert model.external_id == 'test'
        assert model.name == 'test-repo'
        assert model.head_sha == '2'
        assert model.previous_head_sha == '1'
        assert len(model.commits) == 2
        assert model.last_pusher == 'test-user'
        assert model.last_update == '2017-02-02T15:25:43.511Z'

    def doesnt_apply_unrelated_event(self):
        event = Container()
        event.type = 'PipelineStarted'
        event.body = {
            'timestamp': '2017-02-02T14:25:43.511Z'
        }

        model = RepositoryModel(external_id='test',
                                name="hello",
                                last_pusher='old-user',
                                head_sha='123',
                                previous_head_sha='234',
                                last_update='2017-02-02T12:25:43.511Z',
                                commits=[{"test_commit": "hej"}])
        apply_events(RepositoryProjection.apply_event_to_model,
                     model,
                     [event])

        assert model.external_id == 'test'
        assert model.name == 'hello'
        assert last_pusher == 'old-user'

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
