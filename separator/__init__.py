from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

# package import
from separator.config import Config


session = Session()
db = SQLAlchemy()


def create_config_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    session.init_app(app)

    from separator.main.routes import main

    app.register_blueprint(main)
    return app
