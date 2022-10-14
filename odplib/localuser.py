from dataclasses import dataclass
from typing import Optional


@dataclass
class LocalUser:
    """Represents a client-side, logged-in user. Compatible with Flask-Login."""

    id: str
    name: str
    email: str
    active: bool
    verified: bool
    picture: Optional[str]
    role_ids: list[str]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.active and self.verified

    def get_id(self):
        return self.id
