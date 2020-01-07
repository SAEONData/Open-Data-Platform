import click
from flask.cli import with_appcontext

import odpaccounts.models


def init_app(app):
    app.cli.add_command(init_db_command)


@click.command('initdb')
@click.option('--drop-all', is_flag=True)
@with_appcontext
def init_db_command(drop_all):
    if drop_all:
        odpaccounts.models.drop_all()
    odpaccounts.models.create_all()
    click.echo("Initialized the database.")
