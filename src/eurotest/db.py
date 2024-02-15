import sqlite3

import click


def get_db(app):
    db = sqlite3.connect(
        app.config['DATABASE'],
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row

    return db


def init_db(app):
    db = get_db(app)

    with open(f"{app.instance_path}/schema.sql", mode="r") as file:
        db.cursor().executescript(file.read())


def init_app(app):
    # app.do_teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        init_db(app)
        click.echo('Initialized the database.')

    return app



