from ngcd_common.model import Event, Pipeline as PipelineModel, PipelineStage as PipelineStageModel, Repository as RepositoryModel
from copy import deepcopy

class Projection(object):
    @classmethod
    def get_interesting_events(cls):
        raise NotImplementedError("get_interesting_events needs to be implemented in inheriting class!")

    @classmethod
    def get_external_id_from_body(cls, body):
        raise NotImplementedError("get_external_id_from_body needs to be implemented in inheriting class!")

    @classmethod
    def handle_event(cls, session, event):
        raise NotImplementedError("handle_event needs to be implemented in inheriting class!")

    @classmethod
    def get_or_create_with_external_id(cls, external_id, model_cls):
        model = model_cls.query \
                .filter(model_cls.external_id==external_id) \
                .first()

        if not model:
            model = model_cls(external_id=external_id)

        return model

class RepositoryProjection(Projection):
    @classmethod
    def get_interesting_events(cls):
        return ['CodePushed']

    @classmethod
    def get_external_id_from_body(cls, body):
        return body['repositoryName']

    @classmethod
    def handle_event(cls, session, event):
        repo = cls.get_or_create_with_external_id(cls.get_external_id_from_body(event.body), RepositoryModel)

        if event.type == 'CodePushed':
            repo.name = event.body['repositoryName']
            repo.head_sha = event.body['newHeadSha']
            repo.previous_head_sha = event.body['previousHeadSha']
            repo.last_pusher = event.body['pusher']
            repo.commits = event.body['commits']
            repo.last_update = event.body['timestamp']

        session.merge(repo)

class PipelineStageProjection(Projection):
    @classmethod
    def get_interesting_events(cls):
        return ['PipelineStageStarted', 'PipelineStageFinished']

    @classmethod
    def get_external_id_from_body(cls, body):
        return body['uuid']

    @classmethod
    def handle_event(cls, session, event):
        pipeline_stage = cls.get_or_create_with_external_id(cls.get_external_id_from_body(event.body), PipelineStageModel)

        if event.type == 'PipelineStageStarted':
            pipeline_stage.currently_running = True
            pipeline_stage.started_running_at = event.body['timestamp']
        elif event.type == 'PipelineStageFinished':
            pipeline_stage.currently_running = False
            pipeline_stage.result = event.body['result']
            pipeline_stage.finished_running_at = event.body['timestamp']

        pipeline_stage.pipeline_id = event.body['pipelineUuid']
        pipeline_stage.last_update = event.body['timestamp']
        session.merge(pipeline_stage)

class PipelineProjection(Projection):
    @classmethod
    def get_interesting_events(cls):
        return ['PipelineStarted', 'PipelineFinished']

    @classmethod
    def get_external_id_from_body(cls, body):
        return body['uuid']

    @classmethod
    def handle_event(cls, session, event):
        pipeline = cls.get_or_create_with_external_id(cls.get_external_id_from_body(event.body), PipelineModel)

        if event.type == 'PipelineStarted':
            pipeline.currently_running = True
            pipeline.started_running_at = event.body['timestamp']
        elif event.type == 'PipelineFinished':
            pipeline.currently_running = False
            pipeline.result = event.body['result']
            pipeline.finished_running_at = event.body['timestamp']

        pipeline.last_update = event.body['timestamp']
        session.merge(pipeline)
