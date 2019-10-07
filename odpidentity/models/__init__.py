from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    from .hydra_token import HydraToken
    from .user import User
    from .user_role import UserRole
    from .user_institution import UserInstitution
    from .role import Role
    from .scope import Scope
    from .role_scope import RoleScope
    from .institution import Institution
    from .institution_registry import InstitutionRegistry
    db.init_app(app)
