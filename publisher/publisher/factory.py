from flask import Flask, g
from werkzeug.utils import find_modules, import_string
from publisher.blueprints import publisher
from .config import Configuration

def create_app():
    app = Flask('publisher')
    app.config.from_object(Configuration)
    register_blueprints(app)
    register_teardowns(app)

    return app

def register_blueprints(app):
    for name in find_modules('publisher.blueprints'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None

def register_teardowns(app):
    @app.teardown_appcontext
    def close_rabbitmq_connection(error):
        if hasattr(g, 'rabbitmq'):
            g.rabbitmq.close()
