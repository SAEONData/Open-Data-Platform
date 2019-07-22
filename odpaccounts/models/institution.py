from . import db


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    registry_id = db.Column(db.Integer, db.ForeignKey('institution_registry.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return '<Institution %r>' % self.name
