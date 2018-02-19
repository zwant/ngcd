from ngcd_common import model
from flask import Blueprint, jsonify, abort, request, g, current_app
from event_api.factory import get_projector, get_projection_db_session

# create our blueprint :)
bp = Blueprint('events', __name__)

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
    pipeline = projector.backend.get_one_by_external_id(external_id, model.Pipeline)
    if not pipeline:
        abort(404)

    stages = projector.backend.get_by_filter(model.PipelineStage, {"pipeline_id": pipeline.external_id})
    return jsonify({"pipeline": pipeline.as_dict(),
                    "stages": [stage.as_dict() for stage in stages]})

@bp.route("/pipeline_stage/<pipeline_external_id>/<external_id>/")
def pipeline_stage(pipeline_external_id=None, external_id=None):
    """
    swagger_from_file: event_api/blueprints/swagger_docs/pipeline_stage.yaml

    """
    projector = get_projector(current_app)
    projector.process_events()
    stage = projector.backend.get_one_by_filter(model.PipelineStage,
                                                {"pipeline_id": pipeline_external_id,
                                                 "external_id": external_id})
    if not stage:
        abort(404)
    return jsonify(stage.as_dict())

@bp.route("/repository/")
def repository():
    """
    swagger_from_file: event_api/blueprints/swagger_docs/repository.yaml

    """
    repo_id = request.args.get('id')
    projector = get_projector(current_app)
    projector.process_events()
    repository = projector.backend.get_one_by_filter(model.Repository,
                                                     {"full_name": repo_id})
    if not repository:
        abort(404)
    return jsonify(repository.as_dict())

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
    pr = projector.backend.get_one_by_external_id(external_id, model.PullRequest)
    if not pr:
        abort(404)
    return jsonify(pr.as_dict())
