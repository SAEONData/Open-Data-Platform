from sqlalchemy import Column, String, JSON

from odp.db import Base
from odp.db.models.metadata_status import CatalogueStatusMixin


class DataciteStatus(Base, CatalogueStatusMixin):
    __tablename__ = 'datacite_status'

    doi = Column(String, unique=True)
    datacite_record = Column(JSON)
