from ngcd_common import model
from flask import Blueprint, jsonify, abort, request, g, current_app
from event_api.factory import get_projector, get_projector_backend, get_projection_db_session

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
    get_projector(current_app).process_events()
    projector_backend = get_projector_backend(current_app)
    pipeline = projector_backend.get_one_by_external_id(external_id, model.Pipeline)
    if not pipeline:
        abort(404)

    stages = projector_backend.get_by_filter(model.PipelineStage, {"pipeline_id": pipeline.external_id})
    return jsonify({"pipeline": pipeline.as_dict(),
                    "stages": [stage.as_dict() for stage in stages]})

@bp.route("/pipeline_stage/<pipeline_external_id>/<external_id>/")
def pipeline_stage(pipeline_external_id=None, external_id=None):
    """
    swagger_from_file: event_api/blueprints/swagger_docs/pipeline_stage.yaml

    """
    get_projector(current_app).process_events()
    projector_backend = get_projector_backend(current_app)
    stage = projector_backend.get_one_by_filter(model.PipelineStage,
                                                {"pipeline_id": pipeline_external_id,
                                                 "external_id": external_id})
    if not stage:
        abort(404)
    return jsonify(stage.as_dict())

@bp.route("/repository/<repo_name>/")
def repository(repo_name=None):
    """
    swagger_from_file: event_api/blueprints/swagger_docs/repository.yaml

    """
    get_projector(current_app).process_events()
    projector_backend = get_projector_backend(current_app)
    repository = projector_backend.get_one_by_filter(model.Repository,
                                                     {"short_name": repo_name})
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
