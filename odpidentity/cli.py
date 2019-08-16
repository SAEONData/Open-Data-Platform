import click
from flask.cli import with_appcontext

from .models import db


def init_app(app):
    app.cli.add_command(init_db_command)


@click.command('initdb')
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo("Initialized the database.")
