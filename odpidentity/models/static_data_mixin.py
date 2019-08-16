from . import db


class StaticDataMixin:
    """
    Flask-SQLAlchemy declarative mixin for static data models.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)
