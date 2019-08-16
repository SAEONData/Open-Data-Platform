from . import db
from .static_data_mixin import StaticDataMixin


class InstitutionRegistry(StaticDataMixin, db.Model):
    """
    Model representing an institution registry.
    """

    institutions = db.relationship('Institution',
                                   back_populates='registry',
                                   passive_deletes=True,
                                   order_by='institution.title')
