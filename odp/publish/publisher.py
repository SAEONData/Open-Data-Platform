import logging
from datetime import datetime, timezone
from typing import Tuple

from sqlalchemy import or_, and_

from odp.db import transactional_session
from odp.db.models import MetadataStatus
from odp.publish.catalogue import Catalogue
from odp.publish.harvester import Harvester

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(
            self,
            harvester: Harvester,
            *catalogues: Catalogue,
            batch_size: int,
            max_retries: int,
    ):
        self.harvester: Harvester = harvester
        self.catalogues: Tuple[Catalogue, ...] = catalogues
        self.batch_size = batch_size
        self.max_retries = max_retries

    def run(self):
        harvested = 0
        updated = 0
        try:
            for record in self.harvester.getrecords():
                with transactional_session() as session:
                    mdstatus = session.query(MetadataStatus).get(record.id)
                    if mdstatus is None:
                        mdstatus = MetadataStatus(metadata_id=record.id)

                    mdstatus.checked = (now := datetime.now(timezone.utc))
                    if mdstatus.catalogue_record != (catalogue_record := record.dict()):
                        mdstatus.catalogue_record = catalogue_record
                        mdstatus.published = record.published
                        mdstatus.updated = now
                        updated += 1

                    session.add(mdstatus)

                harvested += 1
                self.harvester.setchecked(record.id)
        finally:
            logger.info(f"Harvested {harvested} records from {self.harvester.name}; {updated} records were added/updated")

        for catalogue in self.catalogues:
            synced = 0
            try:
                with transactional_session() as session:
                    syncable_ids = session.query(MetadataStatus.metadata_id).outerjoin(catalogue.model).filter(or_(
                        catalogue.model.metadata_id == None,
                        catalogue.model.checked < MetadataStatus.updated,
                        and_(catalogue.model.error != None, catalogue.model.retries < self.max_retries),
                    )).limit(self.batch_size).all()

                logger.info(f"Selected {len(syncable_ids)} records to sync with {catalogue.name}")
                for (record_id,) in syncable_ids:
                    synced += catalogue.syncrecord(record_id)
            finally:
                logger.info(f"Synced {synced} records with {catalogue.name}")
