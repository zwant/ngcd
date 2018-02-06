from flask import Flask, g
from werkzeug.utils import find_modules, import_string
from event_api.sqlalchemy_patch import SQLAlchemy
from event_api.config import Configuration

db = SQLAlchemy()

def create_app():
    from ngcd_common.model import Base

    app = Flask('event_api')
    app.config.from_object(Configuration)

    from ngcd_common.model import Pipeline, PipelineStage, Repository

    db.init_app(app)
    db.register_base(Base)
    with app.app_context():
        if app.config['CLEAN_DB'] == True:
            print('Cleaning DB')
            Pipeline.__table__.drop(db.session.bind, checkfirst=True)
            PipelineStage.__table__.drop(db.session.bind, checkfirst=True)
            Repository.__table__.drop(db.session.bind, checkfirst=True)
        else:
            print('Not cleaning DB')
        Pipeline.__table__.create(db.session.bind, checkfirst=True)
        PipelineStage.__table__.create(db.session.bind, checkfirst=True)
        Repository.__table__.create(db.session.bind, checkfirst=True)

    register_blueprints(app)
    register_swagger_ui(app)

    return app

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
