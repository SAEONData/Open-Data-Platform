from . import db


class InstitutionRegistry(db.Model):
    """
    Model representing an institution registry.
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)

    institutions = db.relationship('Institution',
                                   back_populates='registry',
                                   passive_deletes=True)

    def __repr__(self):
        return '<InstitutionRegistry %s>' % self.code
