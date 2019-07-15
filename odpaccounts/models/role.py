from . import db


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)

    def __repr__(self):
        return '<Role %r>' % self.name
