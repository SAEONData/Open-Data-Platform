def init_app(app):
    from odpaccounts.db import session
    from odpaccounts.models.user import User
    from odpaccounts.models.member import Member
    from odpaccounts.models.privilege import Privilege
    from odpaccounts.models.role import Role
    from odpaccounts.models.scope import Scope
    from odpaccounts.models.capability import Capability
    from odpaccounts.models.institution import Institution
    from odpaccounts.models.institution_registry import InstitutionRegistry
    from .hydra_token import HydraToken

    # ensure that the db session is closed and disposed after each request
    @app.teardown_appcontext
    def discard_session(exc):
        session.remove()
