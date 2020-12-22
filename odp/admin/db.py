def init_app(app):
    from odp.db import session

    @app.teardown_request
    def release_db_resources(exc):
        """Release DB transaction/connection resources at the end of a request."""
        session.remove()
