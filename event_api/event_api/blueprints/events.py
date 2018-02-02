from ngcd_common import model
from ngcd_common.projector import Projector
from ngcd_common.projections import PipelineProjection, PipelineStageProjection
from flask import Blueprint, jsonify, abort
from event_api.factory import db

# create our blueprint :)
bp = Blueprint('events', __name__)


@bp.route("/pipeline/<external_id>/")
def pipeline(external_id=None):
    projector = Projector(db.session)
    projector.process_events()
    pipeline = model.Pipeline.query \
                .filter(model.Pipeline.external_id == external_id) \
                .first()
    if not pipeline:
        abort(404)

    stages = model.PipelineStage.query \
                .filter(model.PipelineStage.pipeline_id == pipeline.external_id) \
                .order_by(model.PipelineStage.last_update.asc()) \
                .all()

    return jsonify({"pipeline": pipeline.as_dict(),
                    "stages": [stage.as_dict() for stage in stages]})

@bp.route("/pipeline_stage/<external_id>/")
def pipeline_stage(external_id=None):
    projector = Projector(db.session)
    projector.process_events()
    stages = model.PipelineStage.query \
                .filter(model.PipelineStage.external_id == external_id) \
                .order_by(model.PipelineStage.last_update.asc()) \
                .all()
    if not stages:
        abort(404)
    return jsonify([stage.as_dict() for stage in stages])

@bp.route("/repository/<repo_name>/")
def repository(repo_name=None):
    projector = Projector(db.session)
    projector.process_events()
    repository = model.Repository.query \
                .filter(model.Repository.name == repo_name) \
                .first()
    if not repository:
        abort(404)
    return jsonify(repository.as_dict())
