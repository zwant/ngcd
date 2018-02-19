from flask import Flask, g
from werkzeug.utils import find_modules, import_string
from publisher.blueprints import publisher
from .config import Configuration
import logging
import logging.config
import sys
import os
import yaml

def create_app():
    app = Flask('publisher')
    app.config.from_object(Configuration)
    register_blueprints(app)
    register_teardowns(app)
    setup_logging(app)
    return app

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
            g.rabbitmq.release()
