from flask import Flask
from recon.config import Config


def create_config_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    from separator.main.routes import main

    app.register_blueprint(main)
    return app
