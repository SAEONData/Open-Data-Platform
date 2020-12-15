def init_app(app):
    from odp.db import session

    @app.after_request
    def commit_transaction(response):
        """Commit any pending DB transaction after a successful request."""
        if response.status_code < 400:
            try:
                session.commit()
            except Exception:
                session.rollback()
                raise

        return response

    @app.teardown_request
    def release_db_resources(exc):
        """Release DB transaction/connection resources at the end of a request,
        regardless of whether or not an exception occurred."""
        session.remove()
