from typing import Iterator

from odp.api.models.catalogue import CatalogueRecord


class Harvester:
    @property
    def name(self) -> str:
        return self.__class__.__name__.replace('Harvester', '')

    def getrecords(self) -> Iterator[CatalogueRecord]:
        raise NotImplementedError

    def setchecked(self, record_id: str) -> None:
        raise NotImplementedError
