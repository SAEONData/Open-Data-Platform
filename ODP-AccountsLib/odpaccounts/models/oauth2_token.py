from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy_utils import JSONType

from . import Base


class OAuth2Token(Base):
    """
    Represents the OAuth2 token for a logged in user.

    ``provider`` indicates the application for which the token is valid.
    """
    __tablename__ = 'oauth2_token'
    __table_args__ = (UniqueConstraint('provider', 'user_id'),)

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False, index=True)
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User')
    token = Column(MutableDict.as_mutable(JSONType), nullable=False)
