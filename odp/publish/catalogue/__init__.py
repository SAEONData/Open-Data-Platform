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

        :return: True indicates that the catalogue was updated (even if
            it was a partial, failed update); False that an update was not
            required
        """
        raise NotImplementedError
