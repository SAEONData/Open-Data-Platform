from typing import Type

from odp.db.models import ElasticsearchStatus
from odp.db.models.metadata_status import CatalogueStatusMixin
from odp.publish.catalogue import Catalogue


class ElasticsearchCatalogue(Catalogue):
    @property
    def model(self) -> Type[CatalogueStatusMixin]:
        return ElasticsearchStatus

    def syncrecord(self, record_id: str) -> bool:
        return False
