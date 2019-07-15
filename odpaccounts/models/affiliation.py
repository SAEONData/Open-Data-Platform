from . import db

affiliation = db.Table(
    'affiliation',
    db.Column('user_id', db.String, db.ForeignKey('user.id'), primary_key=True),
    db.Column('institution_id', db.Integer, db.ForeignKey('institution.id'), primary_key=True),
)
