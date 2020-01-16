"""
Contains application factory and tells Python that flaskr dir is a package.
"""
from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    """
    Flask application is instance of Flask class.
    Everything about app: configuration, URLS, etc. are registered with this class.
    Instead of creating Flask instance globally, create it inside function.
    This function is known as ~application factory~.
    Configuration, registration, and other setup will happen inside and application will be returned.
    """
    # instance_relative_config tells app configuration files are relative to instance folder
    # instance folder is outisde the flaskr package and can hold local data that shouldn't be committed
    app = Flask(__name__, instance_relative_config=True)
    # default config
    app.config.from_object('config.default')
    if test_config is None:
        # secret stuff that shouldn't be committed goes into instance/config.py
        app.config.from_pyfile('config.py')
        # env var to absolute path of env specific config
        app.config.from_envvar('APP_CONFIG_FILE')
    else:
        app.config.from_mapping(test_config)

    # CORS
    CORS(app)

    # register the blueprint so that all the routes defined in flaskr/views/home.py
    # are registered with app just as if it had been done with @app.route()
    from .views.home import bp
    app.register_blueprint(bp)

    from . import models
    models.setup_db(app)

    return app
