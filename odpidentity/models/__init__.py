from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    from .hydra_token import HydraToken
    from .user import User
    from .member import Member
    from .privilege import Privilege
    from .role import Role
    from .scope import Scope
    from .capability import Capability
    from .institution import Institution
    from .institution_registry import InstitutionRegistry
    db.init_app(app)
