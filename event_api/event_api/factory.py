from flask import Flask, g
from werkzeug.utils import find_modules, import_string
from event_api.sqlalchemy_patch import SQLAlchemy
from event_api import config

db = SQLAlchemy()

def create_app(config_filename):
    from ngcd_common.model import Base

    app = Flask('event_api')
    app.config.from_pyfile(config_filename)

    from ngcd_common.model import Pipeline, PipelineStage, Repository

    db.init_app(app)
    db.register_base(Base)
    with app.app_context():
        Pipeline.__table__.drop(db.session.bind, checkfirst=True)
        PipelineStage.__table__.drop(db.session.bind, checkfirst=True)
        Repository.__table__.drop(db.session.bind, checkfirst=True)
        Pipeline.__table__.create(db.session.bind, checkfirst=True)
        PipelineStage.__table__.create(db.session.bind, checkfirst=True)
        Repository.__table__.create(db.session.bind, checkfirst=True)

    register_blueprints(app)

    return app

def register_blueprints(app):
    from event_api.blueprints import events
    for name in find_modules('event_api.blueprints'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None
