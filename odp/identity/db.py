def init_app(app):
    from odp.db import session

    # import all DB models so that SQLAlchemy can set up relationships
    from odp.db.models.user import User
    from odp.db.models.member import Member
    from odp.db.models.privilege import Privilege
    from odp.db.models.role import Role
    from odp.db.models.scope import Scope
    from odp.db.models.capability import Capability
    from odp.db.models.institution import Institution

    # ensure that the db session is closed and disposed after each request
    @app.teardown_appcontext
    def discard_session(exc):
        session.remove()
