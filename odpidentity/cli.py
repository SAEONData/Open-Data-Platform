import click
from flask.cli import with_appcontext


def init_app(app):
    app.cli.add_command(init_db)


@click.command('initdb')
@click.option('--drop-all', is_flag=True)
@with_appcontext
def init_db(drop_all):
    """
    Create the tables defined in this service (currently only the token table).
    This should be done after initializing all ODP Accounts tables using the Admin service.
    :param drop_all: issue drop table commands before creating the tables
    """
    from odpaccounts.db import engine
    from .models.hydra_token import HydraToken
    if drop_all:
        HydraToken.__table__.drop(bind=engine)
    HydraToken.__table__.create(bind=engine)
    click.echo("Initialized the database.")
