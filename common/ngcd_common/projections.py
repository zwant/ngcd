from ngcd_common.model import Event, Pipeline as PipelineModel, PipelineStage as PipelineStageModel, Repository as RepositoryModel
from copy import deepcopy


def calculate_average_duration(prev_num_runs, prev_duration_avg, new_duration):
    if prev_num_runs < 1:
        return new_duration

    return ((prev_duration_avg * prev_num_runs) + new_duration)/(prev_num_runs + 1)

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
        return cls.get_or_create_by_query(external_id,
                                          model_cls.query.filter(model_cls.external_id==external_id),
                                          model_cls)

    @classmethod
    def get_or_create_by_query(cls, external_id, query, model_cls):
        model = query.first()

        if not model:
            model = model_cls(external_id=external_id)

        return model

class RepositoryProjection(Projection):
    @classmethod
    def get_interesting_events(cls):
        return ['CodePushed', 'RepositoryAdded', 'RepositoryRemoved']

    @classmethod
    def get_external_id_from_body(cls, body):
        return body['identifier']['fullName']

    @classmethod
    def apply_event_to_model(cls, model, event):
        model.short_name = event.body['identifier']['shortName']
        model.full_name = event.body['identifier']['fullName']
        model.type = event.body['identifier']['repoType']
        if event.type == 'CodePushed':
            model.head_sha = event.body['newHeadSha']
            model.previous_head_sha = event.body['previousHeadSha']
            model.last_pusher = event.body['pusher']
            if not model.commits:
                model.commits = []
            model.commits.append(event.body['commits'])
        elif event.type == 'RepositoryAdded':
            model.description = event.body['description']
            model.html_url = event.body['htmlUrl']
            model.api_url = event.body['apiUrl']
            model.created_by = event.body['performedBy']
        elif event.type == 'RepositoryRemoved':
            model.is_deleted = True
            model.deleted_by = event.body['performedBy']
        model.last_update = event.body['timestamp']

    @classmethod
    def handle_event(cls, session, event):
        repo = cls.get_or_create_with_external_id(cls.get_external_id_from_body(event.body), RepositoryModel)
        cls.apply_event_to_model(repo, event)
        session.merge(repo)

class PipelineStageProjection(Projection):
    @classmethod
    def get_interesting_events(cls):
        return ['PipelineStageStarted', 'PipelineStageFinished']

    @classmethod
    def get_external_id_from_body(cls, body):
        return body['uuid']

    @classmethod
    def apply_event_to_model(cls, model, event):
        if event.type == 'PipelineStageStarted':
            model.currently_running = True
            model.started_running_at = event.body['timestamp']
        elif event.type == 'PipelineStageFinished':
            model.currently_running = False
            model.result = event.body['result']
            model.finished_running_at = event.body['timestamp']
            model.last_duration = event.body['durationMs']
            model.average_duration = calculate_average_duration(model.number_of_runs, model.average_duration, event.body['durationMs'])
            model.number_of_runs = model.number_of_runs + 1

        model.pipeline_id = event.body['pipelineUuid']
        model.last_update = event.body['timestamp']

    @classmethod
    def handle_event(cls, session, event):
        external_id = cls.get_external_id_from_body(event.body)
        query = PipelineStageModel.query.filter(PipelineStageModel.external_id==external_id) \
                                        .filter(PipelineStageModel.pipeline_id==event.body['pipelineUuid'])
        pipeline_stage = cls.get_or_create_by_query(external_id,
                                                    query,
                                                    PipelineStageModel)
        cls.apply_event_to_model(pipeline_stage, event)

        session.merge(pipeline_stage)

class PipelineProjection(Projection):
    @classmethod
    def get_interesting_events(cls):
        return ['PipelineStarted', 'PipelineFinished']

    @classmethod
    def get_external_id_from_body(cls, body):
        return body['uuid']

    @classmethod
    def apply_event_to_model(cls, model, event):
        if event.type == 'PipelineStarted':
            model.currently_running = True
            model.started_running_at = event.body['timestamp']
        elif event.type == 'PipelineFinished':
            model.currently_running = False
            model.result = event.body['result']
            model.finished_running_at = event.body['timestamp']
            model.last_duration = event.body['durationMs']
            model.average_duration = calculate_average_duration(model.number_of_runs, model.average_duration, event.body['durationMs'])
            model.number_of_runs = model.number_of_runs + 1

        model.last_update = event.body['timestamp']

    @classmethod
    def handle_event(cls, session, event):
        pipeline = cls.get_or_create_with_external_id(cls.get_external_id_from_body(event.body), PipelineModel)
        cls.apply_event_to_model(pipeline, event)

        session.merge(pipeline)
