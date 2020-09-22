import logging
from datetime import datetime
from typing import Type

import pydantic

from odp.api.models.datacite import DataciteRecordIn
from odp.db import transactional_session
from odp.db.models import MetadataStatus, DataciteStatus
from odp.db.models.metadata_status import CatalogueStatusMixin
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
            doi_landing_base_url: str,
    ):
        self.datacite = DataciteClient(
            api_url=datacite_api_url,
            username=datacite_username,
            password=datacite_password,
            doi_prefix=doi_prefix,
        )
        self.doi_landing_base_url = doi_landing_base_url

    @property
    def model(self) -> Type[CatalogueStatusMixin]:
        return DataciteStatus

    def syncrecord(self, record_id: str) -> None:
        logger.debug(f"Syncing record {record_id}")

        with transactional_session() as session:
            mdstatus, dcstatus = session.query(MetadataStatus, DataciteStatus).outerjoin(DataciteStatus). \
                filter(MetadataStatus.metadata_id == record_id). \
                one()

            if dcstatus is None:
                dcstatus = DataciteStatus(metadata_id=record_id, published=False)

            doi = mdstatus.catalogue_record['doi']
            try:
                datacite_record = DataciteRecordIn(
                    doi=doi,
                    url=f'{self.doi_landing_base_url}/{record_id}',
                    metadata=mdstatus.catalogue_record['metadata'],
                )
                datacite_record_dict = datacite_record.dict()
            except pydantic.ValidationError:
                datacite_record = None
                datacite_record_dict = None

            publish = mdstatus.published and doi is not None and datacite_record is not None
            updated = False
            try:
                if dcstatus.published and (not publish or dcstatus.doi != doi):
                    # the record is currently published and should be unpublished;
                    # if the DOI has changed, we must also first unpublish the record
                    logger.info(f"Unpublishing record {record_id} with DOI {dcstatus.doi}")
                    self.datacite.unpublish_doi(
                        dcstatus.doi,
                    )
                    dcstatus.published = False
                    dcstatus.updated = datetime.now()
                    updated = True

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
                    dcstatus.updated = datetime.now()
                    updated = True

                if not updated:
                    logger.debug(f"No change for record {record_id}")

                dcstatus.error = None
                dcstatus.retries = None

            except DataciteError as e:
                dcstatus.error = f'{e.status_code}: {e.error_detail}'
                dcstatus.retries = dcstatus.retries + 1 if dcstatus.retries is not None else 0
                logger.error(f"Error syncing record {record_id} with DataCite: {dcstatus.error}")

            dcstatus.checked = datetime.now()
            session.add(dcstatus)
