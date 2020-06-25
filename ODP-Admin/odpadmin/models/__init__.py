def init_app(app):
    from odpaccounts.db import session

    # ensure that the db session is closed and disposed after each request
    @app.teardown_appcontext
    def discard_session(exc):
        session.remove()
