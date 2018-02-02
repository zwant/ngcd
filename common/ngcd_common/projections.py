from ngcd_common.model import Event, Pipeline as PipelineModel, PipelineStage as PipelineStageModel, Repository as RepositoryModel
from copy import deepcopy

class Projection(object):
    external_id = None
    id = None
    last_update = None

    def __init__(self, external_id, id=None, last_update=None):
        self.external_id = external_id
        self.id = id
        self.last_update = last_update

    @classmethod
    def get_interesting_events(cls):
        raise NotImplementedError("get_interesting_events needs to be implemented in inheriting class!")

    @classmethod
    def get_db_model(cls):
        raise NotImplementedError("get_db_model needs to be implemented in inheriting class!")

    @classmethod
    def get_external_id_from_body(cls, body):
        raise NotImplementedError("get_external_id_from_body needs to be implemented in inheriting class!")

    @classmethod
    def handle_event(cls, projection, event):
        to_return = None
        if not projection:
            to_return = cls(cls.get_external_id_from_body(event.body))
        else:
            to_return = deepcopy(projection)

        to_return.last_update = event.body['timestamp']

        cls.apply_event(to_return, event)

        return to_return

class RepositoryProjection(Projection):
    commits = []
    name = None
    last_pusher = None
    head_sha = None
    previous_head_sha = None

    def __init__(self,
                 external_id,
                 id=None,
                 last_update=None,
                 name=None,
                 head_sha=None,
                 previous_head_sha=None,
                 last_pusher=None,
                 commits=None):
        super().__init__(external_id, id=id, last_update=last_update)
        self.name = name
        self.head_sha = head_sha
        self.previous_head_sha = previous_head_sha
        self.last_pusher = last_pusher
        self.commits = commits

    @classmethod
    def get_interesting_events(cls):
        return ['CodePushed']

    @classmethod
    def get_db_model(cls):
        return RepositoryModel

    @classmethod
    def get_external_id_from_body(cls, body):
        return body['repositoryName']

    @classmethod
    def apply_event(cls, projection, event):
        """ Updates this codepushed event, with the given event applied to it """
        if event.type == 'CodePushed':
            projection.name = event.body['repositoryName']
            projection.head_sha = event.body['newHeadSha']
            projection.previous_head_sha = event.body['previousHeadSha']
            projection.last_pusher = event.body['pusher']['email']
            projection.commits = event.body['commits']

class PipelineStageProjection(Projection):
    currently_running = None
    result = None
    pipeline_id = None
    started_running_at = None
    finished_running_at = None

    def __init__(self,
                 external_id,
                 id=None,
                 last_update=None,
                 pipeline_id=None,
                 currently_running=None,
                 result=None,
                 started_running_at=None,
                 finished_running_at=None):
        super().__init__(external_id, id=id, last_update=last_update)
        self.pipeline_id = pipeline_id
        self.currently_running = currently_running
        self.result = result
        self.started_running_at = started_running_at
        self.finished_running_at = finished_running_at

    @classmethod
    def get_interesting_events(cls):
        return ['PipelineStageStarted', 'PipelineStageFinished']

    @classmethod
    def get_db_model(cls):
        return PipelineStageModel

    @classmethod
    def get_external_id_from_body(cls, body):
        return body['uuid']

    def as_dict(self):
        return {
            'external_id': self.external_id,
            'pipeline_id': self.pipeline_id,
            'currently_running': self.currently_running,
            'result': self.result,
            'started_running_at': self.started_running_at,
            'finished_running_at': self.finished_running_at
        }

    @classmethod
    def apply_event(cls, projection, event):
        """ Updates this pipeline stage, with the given event applied to it """
        if event.type == 'PipelineStageStarted':
            projection.pipeline_id = event.body['pipelineUuid']
            projection.currently_running = True
            projection.started_running_at = event.body['timestamp']
        elif event.type == 'PipelineStageFinished':
            projection.currently_running = False
            projection.result = event.body['result']
            projection.finished_running_at = event.body['timestamp']

class PipelineProjection(Projection):
    currently_running = None
    result = None
    started_running_at = None
    finished_running_at = None

    def __init__(self,
                 external_id,
                 id=None,
                 last_update=None,
                 currently_running=None,
                 result=None,
                 started_running_at=None,
                 finished_running_at=None):
        super().__init__(external_id, id=id, last_update=last_update)
        self.currently_running = currently_running
        self.result = result
        self.started_running_at = started_running_at
        self.finished_running_at = finished_running_at

    @classmethod
    def get_interesting_events(cls):
        return ['PipelineStarted', 'PipelineFinished']

    @classmethod
    def get_db_model(cls):
        return PipelineModel

    @classmethod
    def get_external_id_from_body(cls, body):
        return body['uuid']

    def as_dict(self):
        return {
            'external_id': self.external_id,
            'currently_running': self.currently_running,
            'result': self.result,
            'started_running_at': self.started_running_at,
            'finished_running_at': self.finished_running_at
        }

    @classmethod
    def apply_event(cls, projection, event):
        """ Updates this pipeline, with the given event applied to it """
        if event.type == 'PipelineStarted':
            projection.currently_running = True
            projection.started_running_at = event.body['timestamp']
        elif event.type == 'PipelineFinished':
            projection.currently_running = False
            projection.result = event.body['result']
            projection.finished_running_at = event.body['timestamp']
