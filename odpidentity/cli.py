import click
from flask.cli import with_appcontext

from .models import init_db


def init_app(app):
    app.cli.add_command(init_db_command)


@click.command('initdb')
@click.option('--drop-all', is_flag=True)
@with_appcontext
def init_db_command(drop_all):
    init_db(drop_all)
    click.echo("Initialized the database.")
