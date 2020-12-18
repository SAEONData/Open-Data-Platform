def init_app(app):
    from odp.db import session

    @app.middleware('http')
    async def release_db_resources(request, call_next):
        """Release DB transaction/connection resources at the end of a request."""
        response = await call_next(request)
        session.remove()
        return response
