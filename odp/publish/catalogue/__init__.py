from typing import Type

from odp.db.models.metadata_status import CatalogueStatusMixin


class Catalogue:
    @property
    def model(self) -> Type[CatalogueStatusMixin]:
        raise NotImplementedError

    def syncrecord(self, record_id: str) -> None:
        raise NotImplementedError
