from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from odp.db import Base


class OAuth2Token(Base):
    """
    Represents the OAuth2 token for a logged in user.
    """
    __tablename__ = 'oauth2_token'
    __table_args__ = (UniqueConstraint('client_id', 'user_id'),)

    id = Column(Integer, primary_key=True)
    client_id = Column(String, nullable=False)  # todo: foreign key ref to client
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
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
