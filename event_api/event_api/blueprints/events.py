from ngcd_common import model
from flask import Blueprint, jsonify, abort, request, g, current_app
from event_api.factory import get_projector, get_projection_db_session, dispose_event_db_session, dispose_projection_db_session

# create our blueprint :)
bp = Blueprint('events', __name__)

@bp.teardown_request
def shutdown_session(exception=None):
    dispose_event_db_session(current_app)
    dispose_projection_db_session(current_app)

@bp.route("/replay/", methods=['POST'])
def replay():
    payload = request.get_json(force=True)
    if 'events' in payload:
        events_to_replay = payload['events']
    else:
        events_to_replay = None
    get_projector(current_app).process_events(only=events_to_replay)

    return "Done!"

@bp.route("/pipeline/<external_id>/")
def pipeline(external_id=None):
    """
    swagger_from_file: event_api/blueprints/swagger_docs/pipeline.yaml

    """
    projector = get_projector(current_app)
    projector.process_events()
    pipeline = projector.projection_backend.get_one_by_external_id(external_id, model.Pipeline)
    if not pipeline:
        abort(404)

    stages = projector.projection_backend.get_by_filter(model.PipelineStage, {"pipeline_id": pipeline.external_id})
    return jsonify({"pipeline": pipeline.as_dict(),
                    "stages": [stage.as_dict() for stage in stages]})

@bp.route("/pipeline/")
def all_pipelines():
    projector = get_projector(current_app)
    projector.process_events()
    pipelines = projector.projection_backend.get_all(model.Pipeline)

    return jsonify({"pipelines": [pipeline.as_dict() for pipeline in pipelines]})

@bp.route("/pipeline_stage/<pipeline_external_id>/<external_id>/")
def pipeline_stage(pipeline_external_id=None, external_id=None):
    """
    swagger_from_file: event_api/blueprints/swagger_docs/pipeline_stage.yaml

    """
    projector = get_projector(current_app)
    projector.process_events()
    stage = projector.projection_backend.get_one_by_filter(model.PipelineStage,
                                                {"pipeline_id": pipeline_external_id,
                                                 "external_id": external_id})
    if not stage:
        abort(404)
    return jsonify(stage.as_dict())

@bp.route("/pipeline_stage/")
def all_pipeline_stages():
    projector = get_projector(current_app)
    projector.process_events()
    pipeline_stages = projector.projection_backend.get_all(model.PipelineStage)

    return jsonify({"pipeline_stages": [pipeline_stage.as_dict() for pipeline_stage in pipeline_stages]})

@bp.route("/repository/")
def repository():
    """
    swagger_from_file: event_api/blueprints/swagger_docs/repository.yaml

    """
    repo_id = request.args.get('id')
    projector = get_projector(current_app)
    projector.process_events()
    if repo_id:
        repository = projector.projection_backend.get_one_by_filter(model.Repository,
                                                         {"full_name": repo_id})
        if not repository:
            abort(404)
        return jsonify(repository.as_dict())
    else:
        repositories = projector.projection_backend.get_all(model.Repository)
        return jsonify({"repositories": [repository.as_dict() for repository in repositories]})


@bp.route("/commit/<sha>/")
def commit(sha=None):
    get_projector(current_app).process_events()
    repos = model.Repository.query \
                .filter(model.Repository.commits.contains([{'sha': sha}])).all()
    if not repos:
        abort(404)
    return jsonify([repo.as_dict() for repo in repos])

@bp.route("/pull_request/<id>/")
def pull_request(id=None):
    repo_id = request.args.get('repo')
    external_id = '{}/{}'.format(repo_id, id)
    projector = get_projector(current_app)
    projector.process_events()
    pr = projector.projection_backend.get_one_by_external_id(external_id, model.PullRequest)
    if not pr:
        abort(404)
    return jsonify(pr.as_dict())

@bp.route("/pull_request/")
def all_pull_requests():
    projector = get_projector(current_app)
    projector.process_events()
    pull_requests = projector.projection_backend.get_all(model.PullRequest)

    return jsonify({"pull_requests": [pull_request.as_dict() for pull_request in pull_requests]})
