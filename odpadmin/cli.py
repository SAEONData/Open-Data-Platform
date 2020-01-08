import click
from flask.cli import with_appcontext


def init_app(app):
    app.cli.add_command(init_db)


@click.command('initdb')
@click.option('--drop-all', is_flag=True)
@with_appcontext
def init_db(drop_all):
    import odpaccounts.models
    if drop_all:
        odpaccounts.models.drop_all()
    odpaccounts.models.create_all()
    click.echo("Initialized the database.")
