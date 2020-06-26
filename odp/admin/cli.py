import click
from flask.cli import with_appcontext


def init_app(app):
    app.cli.add_command(init_db)


@click.command('initdb')
@click.option('--drop-all', is_flag=True)
@with_appcontext
def init_db(drop_all):
    """
    Create all the tables defined in ODP-AccountsLib, as well as the token table
    defined in this service.
    :param drop_all: if this flag is set, drop all tables first, before issuing create table commands
    """
    from odp.db.models import Base
    from odp.db import engine
    if drop_all:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    click.echo("Initialized the database.")
