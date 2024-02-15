import os
from quart import Quart

from . import db

def create_app(test_config=None):
    # create and configure the app
    app = Quart(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'database.sqlite'),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app = db.init_app(app)

    return app
