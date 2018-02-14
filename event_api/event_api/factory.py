from flask import Flask, g
from werkzeug.utils import find_modules, import_string
from event_api.sqlalchemy_patch import SQLAlchemy
from event_api.config import Configuration
import logging
import logging.config
import sys
import os
import yaml

db = SQLAlchemy()

def create_app():
    from ngcd_common.model import Base

    app = Flask('event_api')
    app.config.from_object(Configuration)
    setup_logging(app)

    from ngcd_common.model import Pipeline, PipelineStage, Repository

    db.init_app(app)
    db.register_base(Base)

    with app.app_context():
        if app.config['PROJECTION_STORE_BACKEND'] == 'postgres':
            if app.config['CLEAN_DB'] == True:
                app.logger.info('Cleaning DB')
                Pipeline.__table__.drop(db.session.bind, checkfirst=True)
                PipelineStage.__table__.drop(db.session.bind, checkfirst=True)
                Repository.__table__.drop(db.session.bind, checkfirst=True)
            else:
                app.logger.info('Not cleaning DB')
            Pipeline.__table__.create(db.session.bind, checkfirst=True)
            PipelineStage.__table__.create(db.session.bind, checkfirst=True)
            Repository.__table__.create(db.session.bind, checkfirst=True)

    register_blueprints(app)
    register_swagger_ui(app)


    return app

def get_projector_backend(app):
    from ngcd_common.projections.backends import PostgresBackend, InMemoryBackend

    projection_store_config = app.config['PROJECTION_STORE_BACKEND']
    projector_backend = getattr(g, '_projector_backend', None)
    if projector_backend is None:
        if projection_store_config == 'inmemory':
            projector_backend = g._projector_backend = InMemoryBackend()
        elif projection_store_config == 'postgres':
            projector_backend = g._projector_backend = PostgresBackend(db.session)
        else:
            raise NotImplementedError('No such projection store backend [{}]'.format(projection_store_config))
    return projector_backend

def get_projector(app):
    from ngcd_common.projections.projector import Projector
    backend = get_projector_backend(app)
    projector = getattr(g, '_projector', None)
    if projector is None:
        projector = g._projector = Projector(backend)
    return projector

def setup_logging(app):
    path = app.config['LOGCONFIG']
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
            except Exception as e:
                raise Exception('Failed to read log config from {}'.format(path), e)
    else:
        raise Exception('Failed to read log config from {}'.format(path))
    app.logger
    logging.config.dictConfig(config)


def register_swagger_ui(app):
    from flask_swagger_ui import get_swaggerui_blueprint

    SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
    API_URL = 'http://localhost:5001/api/swagger/'  # Our API url (can of course be a local resource)

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Event API"
        }
    )

    # Register blueprint at URL
    # (URL must match the one given to factory function above)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

def register_blueprints(app):
    from event_api.blueprints import events, swagger
    for name in find_modules('event_api.blueprints'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None
