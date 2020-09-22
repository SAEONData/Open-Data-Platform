from sqlalchemy import Column, String

from odp.db import Base
from odp.db.models.metadata_status import CatalogueStatusMixin


class ElasticsearchStatus(Base, CatalogueStatusMixin):
    __tablename__ = 'elasticsearch_status'

    index = Column(String)
