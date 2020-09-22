from datetime import datetime
from typing import Iterator

from odp.api.models.catalogue import CatalogueRecord


class Harvester:
    def getrecords(self) -> Iterator[CatalogueRecord]:
        raise NotImplementedError

    def setchecked(self, record_id: str, timestamp: datetime) -> None:
        raise NotImplementedError
