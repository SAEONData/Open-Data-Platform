import logging
from datetime import datetime, timezone
from typing import Tuple

import pydantic
from sqlalchemy import or_, and_

from odp.api.models.datacite import DataciteRecordIn
from odp.db import transactional_session
from odp.db.models import MetadataStatus, DataciteStatus
from odp.lib.datacite import DataciteClient
from odp.lib.exceptions import DataciteError
from odp.publish.catalogue import Catalogue

logger = logging.getLogger(__name__)


class DataciteCatalogue(Catalogue):
    def __init__(
            self,
            datacite_api_url: str,
            datacite_username: str,
            datacite_password: str,
            doi_prefix: str,
            doi_landing_page_base_url: str,
            batch_size: int,
            max_retries: int,
    ):
        self.datacite = DataciteClient(
            api_url=datacite_api_url,
            username=datacite_username,
            password=datacite_password,
            doi_prefix=doi_prefix,
        )
        self.doi_landing_page_base_url = doi_landing_page_base_url
        self.batch_size = batch_size
        self.max_retries = max_retries

    def synchronize(self) -> None:
        with transactional_session() as session:
            updated_records = session.query(MetadataStatus.metadata_id, DataciteStatus). \
                outerjoin(DataciteStatus).filter(
                or_(
                    DataciteStatus.metadata_id == None,
                    DataciteStatus.checked < MetadataStatus.updated,
                )
            ).limit(self.batch_size).all()

            # clear errors and retries for updated records
            for record_id, dcstatus in updated_records:
                if dcstatus is not None and dcstatus.error is not None:
                    dcstatus.error = None
                    dcstatus.retries = None

            failed_ids = session.query(MetadataStatus.metadata_id).join(DataciteStatus).filter(
                and_(
                    DataciteStatus.error != None,
                    DataciteStatus.retries < self.max_retries,
                ),
            ).limit(self.batch_size).all()

        syncable_ids = [record_id for record_id, dcstatus in updated_records] + \
                       [record_id for (record_id,) in failed_ids]
        published = 0
        unpublished = 0
        errors = 0
        try:
            logger.info(f"Selected {len(updated_records)} updated records and {len(failed_ids)} "
                        "previously failed records to sync with DataCite")
            for record_id in syncable_ids:
                pub, unpub, err = self._syncrecord(record_id)
                published += pub
                unpublished += unpub
                errors += err
        finally:
            logger.info(f"Published {published} records to DataCite; "
                        f"un-published {unpublished} records from DataCite; "
                        f"{errors} errors")

    def _syncrecord(self, record_id: str) -> Tuple[bool, bool, bool]:
        logger.debug(f"Syncing record {record_id}")
        published = False
        unpublished = False
        error = False

        with transactional_session() as session:
            mdstatus, dcstatus = session.query(MetadataStatus, DataciteStatus).outerjoin(DataciteStatus). \
                filter(MetadataStatus.metadata_id == record_id). \
                one()

            if dcstatus is None:
                dcstatus = DataciteStatus(metadata_id=record_id, published=False)
                session.add(dcstatus)

            doi = mdstatus.catalogue_record['doi']
            try:
                datacite_record = DataciteRecordIn(
                    doi=doi,
                    url=f'{self.doi_landing_page_base_url}/{record_id}',
                    metadata=mdstatus.catalogue_record['metadata'],
                )
                datacite_record_dict = datacite_record.dict()
            except pydantic.ValidationError:
                datacite_record = None
                datacite_record_dict = None

            publish = mdstatus.published and doi is not None and datacite_record is not None
            try:
                if dcstatus.published and (not publish or dcstatus.doi != doi):
                    # the record is currently published and should be unpublished;
                    # if the DOI has changed, we must also first unpublish the record
                    logger.info(f"Unpublishing record {record_id} with DOI {dcstatus.doi}")
                    self.datacite.unpublish_doi(
                        dcstatus.doi,
                    )
                    dcstatus.published = False
                    dcstatus.updated = datetime.now(timezone.utc)
                    unpublished = True

                if publish and (not dcstatus.published or dcstatus.datacite_record != datacite_record_dict):
                    # the record should be published; it is either not currently published,
                    # or it is published but one or more properties has changed
                    logger.info(f"Publishing record {record_id} with DOI {doi}")
                    self.datacite.publish_doi(
                        datacite_record,
                    )
                    dcstatus.doi = doi
                    dcstatus.datacite_record = datacite_record_dict
                    dcstatus.published = True
                    dcstatus.updated = datetime.now(timezone.utc)
                    published = True

                if not (published or unpublished):
                    logger.debug(f"No change for record {record_id}")

                dcstatus.error = None
                dcstatus.retries = None

            except DataciteError as e:
                dcstatus.error = f'{e.status_code}: {e.error_detail}'
                dcstatus.retries = dcstatus.retries + 1 if dcstatus.retries is not None else 0
                logger.error(f"Error syncing record {record_id} with DataCite: {dcstatus.error}")
                error = True

            dcstatus.checked = datetime.now(timezone.utc)

        return published, unpublished, error
