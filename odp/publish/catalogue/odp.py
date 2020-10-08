import logging
from datetime import datetime, timezone

from odp.db import transactional_session
from odp.db.models import MetadataStatus
from odp.publish.catalogue import Catalogue
from odp.publish.harvester import Harvester

logger = logging.getLogger(__name__)


class ODPCatalogue(Catalogue):
    def __init__(self, harvester: Harvester):
        self.harvester = harvester

    def synchronize(self) -> None:
        harvested = 0
        updated = 0
        try:
            for record in self.harvester.getrecords():
                with transactional_session() as session:
                    mdstatus = session.query(MetadataStatus).get(record.id)

                    # only add new records to the catalogue if they're marked as
                    # published in the primary metadata store; if a record is later
                    # un-published, it will be flagged as such to enable external
                    # harvesters to handle as appropriate, but we don't need records
                    # that have never been published appearing in the catalogue
                    if mdstatus is None and record.published:
                        mdstatus = MetadataStatus(metadata_id=record.id)
                        session.add(mdstatus)

                    if mdstatus is not None:
                        mdstatus.checked = (now := datetime.now(timezone.utc))
                        if mdstatus.catalogue_record != (catalogue_record := record.dict(by_alias=True)):
                            mdstatus.catalogue_record = catalogue_record
                            mdstatus.published = record.published
                            mdstatus.updated = now
                            updated += 1

                harvested += 1
                self.harvester.setchecked(record.id)

        except Exception as e:
            logger.critical(str(e))
        finally:
            logger.info(f"Harvested {harvested} records from {self.harvester.name}; "
                        f"{updated} catalogue records were added/updated")
