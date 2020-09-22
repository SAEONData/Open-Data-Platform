from datetime import datetime
from typing import Tuple

from sqlalchemy import or_, and_

from odp.db import transactional_session
from odp.db.models import MetadataStatus
from odp.publish.catalogue import Catalogue
from odp.publish.harvester import Harvester


class Publisher:
    def __init__(
            self,
            harvester: Harvester,
            *catalogues: Catalogue,
            max_retries: int,
    ):
        self.harvester: Harvester = harvester
        self.catalogues: Tuple[Catalogue, ...] = catalogues
        self.max_retries = max_retries

    def run(self):
        for record in self.harvester.getrecords():
            with transactional_session() as session:
                mdstatus = session.query(MetadataStatus).get(record.id)
                if mdstatus is None:
                    mdstatus = MetadataStatus(metadata_id=record.id)

                mdstatus.checked = (now := datetime.now())
                if mdstatus.catalogue_record != (catalogue_record := record.dict()):
                    mdstatus.catalogue_record = catalogue_record
                    mdstatus.published = record.published
                    mdstatus.updated = now

                session.add(mdstatus)

            self.harvester.setchecked(record.id, now)

        for catalogue in self.catalogues:
            with transactional_session() as session:
                syncable_ids = session.query(MetadataStatus.metadata_id).outerjoin(catalogue.model).filter(or_(
                    catalogue.model.metadata_id == None,
                    catalogue.model.checked < MetadataStatus.updated,
                    and_(catalogue.model.error != None, catalogue.model.retries < self.max_retries),
                )).all()

            for (record_id,) in syncable_ids:
                catalogue.syncrecord(record_id)
