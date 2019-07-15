from . import db


class InstitutionRegistry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    url = db.Column(db.String)
    institutions = db.Relationship('Institution', backref='registry', lazy=True)

    def __repr__(self):
        return '<InstitutionRegistry %r>' % self.name
