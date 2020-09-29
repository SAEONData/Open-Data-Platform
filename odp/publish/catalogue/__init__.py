from typing import Type

from odp.db.models.metadata_status import CatalogueStatusMixin


class Catalogue:
    @property
    def name(self) -> str:
        return self.__class__.__name__.replace('Catalogue', '')

    @property
    def model(self) -> Type[CatalogueStatusMixin]:
        raise NotImplementedError

    def syncrecord(self, record_id: str) -> bool:
        """ Publish/unpublish a record to/from the catalogue, if its
        content and/or status has changed with respect to the catalogue.

        :return: True if the catalogue was successfully updated,
            False upon error or if an update was not required
        """
        raise NotImplementedError
