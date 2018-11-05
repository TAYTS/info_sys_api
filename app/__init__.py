import logging
import logging.handlers

from flask import Flask
from flask_session import Session
from flask_login import LoginManager

from models import db

sess = Session()
login_manager = LoginManager()


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

    # Login Manager
    login_manager.session_protection = 'strong'
    login_manager.init_app(app)

    from models import Users

    @login_manager.user_loader
    def load_user(id_user_hash):
        user = db.session.query(
            Users
        ).filter(
            Users.id_user_hash == id_user_hash
        ).first()

        return user

    db.init_app(app)
    sess.init_app(app)

    # Define all the modules
    from app.modules import core
    from app.modules import admin
    from app.modules import inventory

    # Register the blueprint of each module
    app.register_blueprint(core.module)
    app.register_blueprint(admin.module)
    app.register_blueprint(inventory.module)

    return app


app = make_app('config.py')
