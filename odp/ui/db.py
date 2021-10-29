def init_app(app):
    from odp.db import Session

    @app.after_request
    def commit_transaction(response):
        """Commit any open transaction if the request was successful."""
        if 200 <= response.status_code < 400:
            Session.commit()
        else:
            Session.rollback()

        return response

    @app.teardown_request
    def release_db_resources(exc):
        """Release DB transaction/connection resources at the end of a request."""
        Session.remove()
