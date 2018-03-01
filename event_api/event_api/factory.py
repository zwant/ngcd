from ngcd_common.model import ProjectionBase
from flask import Flask, g
from werkzeug.utils import find_modules, import_string
from event_api.config import Configuration
import logging
import logging.config
import sys
import os
import yaml

def create_app():

    app = Flask('event_api')
    app.config.from_object(Configuration)
    setup_logging(app)
    if app.config['PROJECTION_STORE_BACKEND_TYPE'] == 'sqlalchemy':
        setup_db_tables(app)

    register_blueprints(app)
    register_swagger_ui(app)
    setup_cors(app)
    return app

def setup_cors(app):
    from flask_cors import CORS

    CORS(app)

def setup_db_tables(app):
    with app.app_context():
        projection_db_session = get_projection_db_session(app)

        if app.config['CLEAN_PROJECTION_DB'] == True:
            app.logger.info('Cleaning DB')
            ProjectionBase.metadata.drop_all(bind=projection_db_session.get_bind())
        else:
            app.logger.info('Not cleaning DB')

        ProjectionBase.metadata.create_all(bind=projection_db_session.get_bind())
        ProjectionBase.query = get_projection_db_session(app).query_property()

def get_event_db_session(app):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.orm import sessionmaker

    event_db_session = getattr(g, '_event_db_session', None)
    if event_db_session is None:
        db_engine = create_engine(app.config['EVENT_SQLALCHEMY_DATABASE_URI'])
        event_db_session = g._event_db_session = scoped_session(sessionmaker(bind=db_engine))

    return event_db_session

def get_projection_db_session(app):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.orm import sessionmaker

    projection_db_session = getattr(g, '_projection_db_session', None)
    if projection_db_session is None:
        db_engine = create_engine(app.config['PROJECTION_SQLALCHEMY_DATABASE_URI'])

        projection_db_session = g._projection_db_session = scoped_session(sessionmaker(autocommit=False,
                                                                          autoflush=False,
                                                                          bind=db_engine))
    return projection_db_session



def get_projector_backend(app):
    from ngcd_common.projections.projection_backends import SQLAlchemyBackend, InMemoryBackend

    projector_backend = getattr(g, '_projector_backend', None)
    if projector_backend is None:
        projection_store_config = app.config['PROJECTION_STORE_BACKEND_TYPE']
        if projection_store_config == 'inmemory':
            projector_backend = g._projector_backend = InMemoryBackend()
        elif projection_store_config == 'sqlalchemy':
            projector_backend = g._projector_backend = SQLAlchemyBackend(get_projection_db_session(app))
        else:
            raise NotImplementedError('No such projection store backend [{}]'.format(projection_store_config))
    return projector_backend

def get_event_backend(app):
    from ngcd_common.projections.event_backends import SQLAlchemyBackend, DummyBackend

    event_backend = getattr(g, '_event_backend', None)
    if event_backend is None:
        event_store_config = app.config['EVENT_STORE_BACKEND_TYPE']
        if event_store_config == 'dummy':
            event_backend = g._event_backend = DummyBackend()
        elif event_store_config == 'sqlalchemy':
            event_backend = g._event_backend = SQLAlchemyBackend(get_event_db_session(app))
        else:
            raise NotImplementedError('No such event store backend [{}]'.format(event_store_config))
    return event_backend

def get_projector(app):
    from ngcd_common.projections.projector import Projector

    projector_backend = get_projector_backend(app)
    event_backend = get_event_backend(app)
    projector = getattr(g, '_projector', None)
    if projector is None:
        projector = g._projector = Projector(projector_backend, event_backend)
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
