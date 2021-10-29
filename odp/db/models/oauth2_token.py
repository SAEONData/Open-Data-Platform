from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from odp.db import Base


class OAuth2Token(Base):
    """OAuth2 token storage for the ODP UI."""

    __tablename__ = 'oauth2_token'

    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    user = relationship('User')

    token_type = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    id_token = Column(String)
    expires_at = Column(Integer)

    def dict(self):
        return {
            'token_type': self.token_type,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'id_token': self.id_token,
            'expires_at': self.expires_at,
        }
