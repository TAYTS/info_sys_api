import logging
import logging.handlers

from flask import Flask
from flask_session import Session

from models import db

sess = Session()


def make_app(config='config.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config)

    # LOGGING CONSTANTS
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = logging.handlers.RotatingFileHandler(
        app.config['APP_LOG_FILE'], maxBytes=1024 * 1024 * 100, backupCount=20)
    handler.setFormatter(formatter)
    handler.setLevel(app.config['APP_LOG_LEVEL'])
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['APP_LOG_LEVEL'])

    db.init_app(app)
    sess.init_app(app)

    from app.modules import core
    app.register_blueprint(core.module)

    return app


app = make_app('config.py')
